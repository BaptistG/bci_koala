/*
 *      biosemi_talker.cpp
 * 
 * 
 * Programme permettant de diffuser sous ROS les échantillons en provenance
 * du système d'acquisition biosemi.
 * Note : un message est diffusé par échantillon, un échantillon peut
 * contenir plusieurs canaux.
 * 
 * 
 * 
 * Ce programme transmet des messages qui contiennt :
 * - le numéro d'ordre de l'échantillon
 * - la fréquence d'échantillonnage
 * - un tableau de valeurs réelles (double) dont la taille dépend 
 *   des paramètres de lancement du serveur d'acquistion (nombre de canaux)
 * - une chaîne de caractères extra (pour les codes d'erreurs).
 * 
 */

#include "ros/ros.h"
#include "acquisition_biosemi/biosemi_result.h"
#include "acquisition_biosemi/biosemi_echantillon.h"
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>



#define TAILLE_BUFFER 20000
#define FREQUENCE 2048

using namespace std;

static int frequence = FREQUENCE;
static int fin_de_donnees = 0;


/*************************************************************************************************************/

int appelleServeur(int port, char * name);

	// Appelle un serveur par son nom et un numéro de port.
	// Renvoie un numéro de socket, ou -1 si erreur.

int appelleServeur(int port, char * name) {
    struct hostent *hostinfo;
	struct sockaddr_in server;
	int Socket;

	hostinfo=gethostbyname(name);
	if (hostinfo == NULL) return -1;
	bzero((char*)&server, sizeof(server));
    memcpy(&server.sin_addr, hostinfo->h_addr, hostinfo->h_length);
    server.sin_family=AF_INET;
    server.sin_port=htons(port);
    Socket=socket(AF_INET,SOCK_STREAM,0);static int fin_de_donnees = 0;

    if (connect(Socket, (struct sockaddr *)&server, sizeof(server)))
		return -1;
	else
		return Socket;
}

/*************************************************************************************************************/

void lecture_reseau(int socket, char * buffer, int * entree) {
	ssize_t longueur;
	
	if (*entree == 2 * TAILLE_BUFFER) return;
	longueur = recv(socket, buffer + (*entree), 2 * TAILLE_BUFFER - (*entree), 0);
	if (longueur <= 0) {
		fin_de_donnees = 1;
	} else {
		*entree += longueur;
		buffer[*entree] = 0;
	}
}

/*************************************************************************************************************/

int recupere_ligne(acquisition_biosemi::biosemi_echantillon & echantillon, const char * buffer, int & lecture, int & entree) {
	int local_lect = 0;
	int local_fin;
	char * fin;ros::spinOnce();
	double valeur;
	int ok;
	char local_buffer[TAILLE_BUFFER+1];
	int i;
	
	static int compteur = 0;

	
	// Récupération d'une ligne au maximum dans un buffer local.
	for(i = 0; (i+lecture < entree) && (buffer[i+lecture] != '\n') && (buffer[i+lecture] != 0); i++) {
		local_buffer[i] = buffer[i+lecture];
		local_buffer[i+1] = '\0';
	}
	if (buffer[i+lecture] != '\n') return 0;		// Fin de la ligne non trouvée.
	
	// On efface l'ancien contenu :
	echantillon.valeurs.clear();
	echantillon.frequence = frequence;
	echantillon.extra = "";
	
	// Lecture du numéro :
	echantillon.numero = strtoul(local_buffer + local_lect, &fin, 10);
	local_fin = fin - local_buffer;
	// Le caractère suivant est forcément un ':', sinon le numéro n'est pas présent.
	if (local_buffer[local_fin] != ':') {
		compteur += 1;
		echantillon.numero = compteur;
	} else {
		local_lect = local_fin + 1;
	}


	// On scanne des doubles, autant qu'on en trouve :
	do {
		ok = 0;
		valeur = strtod(local_buffer + local_lect, &fin);
		local_fin = fin - local_buffer;
		if (valeur != 0.0) {
			ok = 1;					// Une valeur non nulle indique une conversion correcte.
		} else {
			// Une valeur nulle peut indiquer une conversion incorrecte, ou le fait que le nombre soit nul.
			// Il faut vérifier cela. On doit trouver des chiffres dans l'espace qui a étré scanné.
			ok = 0;
			for(int i = local_lect; i < local_fin; i++) {
				if ((local_buffer[i] >= '0') && (local_buffer[i] <= '9')) ok = 1;	// Il y a des chiffres.
			}
		}
		if (ok) {
			local_lect = local_fin;
			echantillon.valeurs.push_back(valeur);
		}
	} while (ok);


	// On recherche s'il y a encore des caractères sur la ligne :
	while(local_buffer[local_lect] == ' ') local_lect ++;
	echantillon.extra = local_buffer + local_lect;

	lecture += strlen(local_buffer) + 1;
	return 1;									// Ici la ligne a été complètement décodée.
}



/*************************************************************************************************************/

int main(int argc, char **argv)
{
  int Socket;
  char buffer[2 * TAILLE_BUFFER + 1];
  int entree, lecture;
  acquisition_biosemi::biosemi_result msg;
  
  
  // Vérification des paramètres de la ligne de commande :
  
  if (argc < 2) {
	  cerr << "Appel par : biosemi_talker <nom du serveur> [<numéro de port>]." << std::endl;
	  cerr << "        -- le serveur est la machine sous Windows reliée au système d'acquisition." << std::endl;
	  cerr << "        -- le numéro de port par défaut, si non spécifié, est 50000." << std::endl;
	  exit(1);
  }
  
  
  // Initialisation de ROS :
  
  ros::init(argc, argv, "biosemi_talker");
  ros::NodeHandle n;
  ros::Publisher biosemi_pub = n.advertise<acquisition_biosemi::biosemi_result>("biosemi_result", 3);


  // Connexion au serveur réseau :

  Socket = appelleServeur( argc >= 3 ? atoi(argv[2]) : 50000 , argv[1] );
  if (Socket < 0) {
	  cout << "Erreur de connexion au serveur : " << argv[1] << endl;
	  ros::shutdown();
  }
  entree = 0;
  lecture = 0;
  
  
  msg.numero = 0;
  msg.nombre = 0;
  msg.frequence = 0;
  msg.valeurs.clear();
  msg.extra = "";
  while (ros::ok())
  {
	acquisition_biosemi::biosemi_echantillon ech;

	lecture_reseau(Socket, buffer, &entree);

	while(recupere_ligne(ech, buffer, lecture, entree)) {
		if (lecture >= TAILLE_BUFFER) {ros::spinOnce();
			lecture -= TAILLE_BUFFER;
			entree -= TAILLE_BUFFER;
			memcpy(buffer, buffer+TAILLE_BUFFER, TAILLE_BUFFER + 1);
		}
		



		if (msg.numero == 0) msg.numero = ech.numero;
		msg.nombre += 1;
		msg.frequence = ech.frequence;
		if (ech.extra != "") msg.extra = ech.extra;
		for(std::vector<double>::const_iterator i = ech.valeurs.begin(); i != ech.valeurs.end(); ++i)
			msg.valeurs.push_back(*i);

		
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(12);
		std::cout.width(12); std::cout.fill('0');
		std::cout << ech.numero;
		std::cout.width(0); std::cout.fill(' ');
		std::cout << "[" << ech.frequence << "]:  ";
		for(std::vector<double>::const_iterator i = ech.valeurs.begin(); i != ech.valeurs.end(); ++i)
			std::cout << "  " << *i;
		std::cout << "  " << ech.extra << std::endl;
		
		
		
		
		if (msg.nombre == frequence/10) {
			biosemi_pub.publish(msg);
			ros::spinOnce();
			msg.numero = 0;
			msg.nombre = 0;
			msg.frequence = 0;
			msg.valeurs.clear();
			msg.extra = "";
		}
	}
	if (fin_de_donnees) {
		biosemi_pub.publish(msg);
		ros::spinOnce();
		msg.numero = 0;
		msg.nombre = 0;
		msg.frequence = 0;
		msg.valeurs.clear();
		msg.extra = "";
		ros::shutdown();
		std::cerr << "Perte de la connexion réseau." << endl;
	}
  }

  close(Socket);
  return 0;
}
