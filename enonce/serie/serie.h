/****************************************************
 *
 *		serie.h
 *
 *
 *   Copyright (C) 2009,  Supelec
 *
 *   Author : Jean-Louis Gutzwiller
 *
 *
 *   This library is free software; you can redistribute it and/or
 *   modify it under the terms of the GNU Lesser General Public
 *   License as published by the Free Software Foundation; either
 *   version 2.1 of the License, or any later version.
 *   
 *   This library is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *   Lesser General Public License for more details.
 *   
 *   You should have received a copy of the GNU Lesser General Public
 *   License along with this library; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 *   Contact : Jean-Louis.Gutzwiller@supelec.fr
 *
 *
 *-----------------------------------------------------
 *
 *		serie.h
 *
 *
 *		Utilisation d'un port série pour Linux
 *		ou pour Windows.
 *
 *					Version 1.0
 *					Jean-Louis Gutzwiller, le 26 mai 2010
 *
 *
 *******************************************************/



typedef void * portSerie;

// Les fonctions suivantes permettent d'utiliser le port série.
// La fonction d'ouverture prend en paramètre le nom (sous Linux,
// par exemple /dev/ttyUSB0 ; sous Windows par exemple COM1).
//
// Les valeurs possibles :
//
//	--> name : un nom d'un port série qui existe sur la machine
//			(/dev/ttyUSBn pour Linux, COMn pour Windows).
//  --> speed : une vitesse standard : 110, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200.
//	--> bits : 7 ou 8
//  --> parity : 0 ou 1
//		Noter que sur certains systèmes, bits + parity = 8.
// 	--> stops : 10, 15 ou 20 pour 1, 1.5 ou 2 bits de stop.
//
// Les fonctions de réception et d'émission sont bloquantes. Bien que l'ensemble
// de ces fonctions ne soit pas "multi-thread safe", il est possible
// d'utiliser la fonction d'émission et la fonction de réception dans deux
// threads différents.
//
// Les fonctions de lecture et d'écriture renvoient le nombre de caractères
// lus ou écrits.
//
// La fonction d'ouverture dite "bloquante" permet de choisir le fonctionnement
// bloquant ou non de la fonction de lecture. Si le paramètre "bloque" est 1,
// alors la fonction de lecture est bloquante jusqu'à ce que le nombre de caractères
// demandé soit obtenu, sinon, elle est non bloquante et renvoie le nombre de 
// caractères actuellement disponible. Notons que afin d'éviter des boucles
// de consommation de processeur à pleine puissance, la fonction de lecture
// attend 1 ms si le nombre de caractères demandé n'est pas atteint.
// La fonction d'ouverture par défaut utilise l'option bloquante.


#ifdef __cplusplus
extern "C" {
#endif

portSerie ouvrePortSerie(char * nom, int vitesse, int bits, int parite, int stops);
portSerie ouvrePortSerieBloquant(char * nom, int vitesse, int bits, int parite, int stops, int bloque);
void fermePortSerie(portSerie h);
int lecturePortSerie(portSerie h, char * c, int len);
int ecriturePortSerie(portSerie h, char * c, int len);

#ifdef __cplusplus
}
#endif
