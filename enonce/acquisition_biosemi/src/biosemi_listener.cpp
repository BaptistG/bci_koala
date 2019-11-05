#include "ros/ros.h"
#include "acquisition_biosemi/biosemi_result.h"
#include <iostream>


static unsigned long int numero;


/* Cette fonction est appelée à chaque réception de message */
void biosemiCallback(const acquisition_biosemi::biosemi_result msg)
{
	int num, taille;
	
	taille = msg.valeurs.size();
	std::vector<double>::const_iterator i = msg.valeurs.begin();
	for(num = 0; num < msg.nombre; num ++ ) {
		std::cout.setf(std::ios::fixed, std::ios::floatfield);
		std::cout.precision(12);
		std::cout.width(12); std::cout.fill('0');
		std::cout << msg.numero + num;
		std::cout.width(0); std::cout.fill(' ');
		std::cout << "[" << msg.frequence << "]:  ";
		for(int k = 0; k < taille / msg.nombre; k++) {
			std::cout << "  " << *i;
			++i;
		}
		std::cout << "  " << msg.extra << std::endl;


		if (numero != 0) {
			if (msg.numero + num != numero + 1) {
				std::cerr << "Perte de synchronisation : numero = " << msg.numero << ", ancien = " << numero << std::endl;
				ros::shutdown();
			}
		}
		numero = msg.numero + num;
	}
}

int main(int argc, char **argv)
{
  numero = 0;
  ros::init(argc, argv, "biosemi_listener");
  ros::NodeHandle n;
  ros::Subscriber sub = n.subscribe("biosemi_result", 1000, biosemiCallback);

  ros::spin();

  return 0;
}
