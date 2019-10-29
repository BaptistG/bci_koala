/****************************************************
 *
 *		serie.c
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
 *		serie.c
 *
 *
 *		Utilisation d'un port série pour Linux
 *		ou pour Windows.
 *
 *					Version 1.0.1
 *					Jean-Louis Gutzwiller, le 8 novembre 2010
 *
 *
 *******************************************************/


#include "serie.h"


#ifdef _WINDOWS_
#include <windows.h>
#include <stdlib.h>
typedef struct _SERIALHANDLE_ {
	HANDLE windowsHandle;
	int bloque;
} _SERIALHANDLE_;
#endif

#ifdef _LINUX_
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
typedef struct _SERIALHANDLE_ {
	int linuxHandle;
	int bloque;
} _SERIALHANDLE_;
#endif
typedef _SERIALHANDLE_ * _serialHandle_;

/********************************************************************/

portSerie ouvrePortSerieBloquant(char * nom, int vitesse, int bits, int parite, int stops, int bloque) {
#ifdef _WINDOWS_
	DCB dcb;
	BOOL fSuccess;
	_serialHandle_ h;
	COMMTIMEOUTS timeouts;


	h = (_serialHandle_)malloc(sizeof(_serialHandle_*));
	if (h == NULL) return NULL;

	h->bloque = bloque;
	h->windowsHandle = CreateFile(
		nom, 								// Port série
		GENERIC_READ+GENERIC_WRITE,			// En lecture et écriture
		0,									// que pour moi.
		NULL,
		OPEN_EXISTING,						// Ce port existe forcément
		FILE_ATTRIBUTE_NORMAL,
		NULL
	);
	
	
	if (h->windowsHandle == INVALID_HANDLE_VALUE) {
		return NULL;
	}
	
	
	dcb.DCBlength = sizeof(DCB);
	fSuccess = GetCommState(h->windowsHandle, &dcb);

	switch (vitesse) {
		case 110 : dcb.BaudRate = CBR_110; break;
		case 300 : dcb.BaudRate = CBR_300; break;
		case 600 : dcb.BaudRate = CBR_600; break;
		case 1200 : dcb.BaudRate = CBR_1200; break;
		case 2400 : dcb.BaudRate = CBR_2400; break;
		case 4800 : dcb.BaudRate = CBR_4800; break;
		case 9600 : dcb.BaudRate = CBR_9600; break;
		case 19200 : dcb.BaudRate = CBR_19200; break;
		case 38400 : dcb.BaudRate = CBR_38400; break;
		case 57600 : dcb.BaudRate = CBR_57600; break;
		case 115200 : dcb.BaudRate = CBR_115200; break;
		default : dcb.BaudRate = CBR_9600; break;
	}
	dcb.fBinary = TRUE;

	dcb.fDtrControl = DTR_CONTROL_DISABLE;
	dcb.fRtsControl = RTS_CONTROL_DISABLE;
	
	dcb.ByteSize = bits;
	dcb.Parity = parite;
	switch (stops) {
		case 10 : dcb.StopBits = ONESTOPBIT; break;
		case 15 : dcb.StopBits = ONE5STOPBITS; break;
		case 20 : dcb.StopBits = TWOSTOPBITS; break;
	}
	
	fSuccess = SetCommState(h->windowsHandle, &dcb);
	if (!fSuccess) {
		CloseHandle(h->windowsHandle);
		free((void*) h);
		return NULL;
	}



	/* Configuration des time outs					*/
	// Le thread de lecture doit impérativement rendre	
	// la main le plus souvent possible, car il n'est
	// pas possible de lire et d'écrire simultanément
	// en multi-thread sous Windows.
	GetCommTimeouts(h->windowsHandle,&timeouts);
	timeouts.ReadIntervalTimeout = 0; 
	timeouts.ReadTotalTimeoutMultiplier = 0;
	timeouts.ReadTotalTimeoutConstant = 1;
	timeouts.WriteTotalTimeoutMultiplier = 0;
	timeouts.WriteTotalTimeoutConstant = 0;
	if (!SetCommTimeouts(h->windowsHandle, &timeouts)) {
		CloseHandle(h->windowsHandle);
		free((void*) h);
		return NULL;
	}




	return (portSerie)h;
#endif

#ifdef _LINUX_
	struct termios myserial;		// man tty_ioctl
	_serialHandle_ h;


	h = (_serialHandle_)malloc(sizeof(_serialHandle_*));
	if (h == NULL) return NULL;

	h->bloque = bloque;
	h -> linuxHandle = open(nom, O_RDWR+(bloque ? 0 : O_NONBLOCK));
	if (h -> linuxHandle == -1) {
		return NULL;
	}

	myserial.c_iflag = IGNBRK+(parite==0?IGNPAR:0);
	myserial.c_oflag = 0;
	switch (vitesse) {
		case 110  : myserial.c_cflag = B110; break;
		case 300  : myserial.c_cflag = B300; break;
		case 600  : myserial.c_cflag = B600; break;
		case 1200  : myserial.c_cflag = B1200; break;
		case 2400  : myserial.c_cflag = B2400; break;
		case 4800  : myserial.c_cflag = B4800; break;
		case 9600  : myserial.c_cflag = B9600; break;
		case 19200  : myserial.c_cflag = B19200; break;
		case 38400 : myserial.c_cflag = B38400; break;
		case 57600 : myserial.c_cflag = B57600; break;
		case 115200 : myserial.c_cflag = B115200; break;
		default : myserial.c_cflag = B9600; break;
	}
	switch (bits) {
		case 5 : myserial.c_cflag += CS5; break;
		case 6 : myserial.c_cflag += CS6; break;
		case 7 : myserial.c_cflag += CS7; break;
		default : myserial.c_cflag += CS8; break;
	}
	myserial.c_cflag += CLOCAL+CREAD;
	if (parite) myserial.c_cflag += PARENB;	
	myserial.c_lflag = 0;

	ioctl(h -> linuxHandle,TCSETS,&myserial);		// man tcgetattr, tcsetattr


	return (portSerie)h;	
#endif
}

/********************************************************************/

portSerie ouvrePortSerie(char * nom, int vitesse, int bits, int parite, int stops) {
	return ouvrePortSerieBloquant(nom, vitesse, bits, parite, stops, 1);
}

/********************************************************************/

void fermePortSerie(portSerie h) {
	if (h == NULL) return;
#ifdef _WINDOWS_
	if (((_serialHandle_)h) -> windowsHandle != INVALID_HANDLE_VALUE)
		CloseHandle(((_serialHandle_)h) -> windowsHandle);
#endif

#ifdef _LINUX_
	if (((_serialHandle_)h) -> linuxHandle >= 0)
		close(((_serialHandle_)h) -> linuxHandle);
#endif

	free((void*)h);
	return;
}

/********************************************************************/

int lecturePortSerie(portSerie h, char * c, int len) {
#ifdef _WINDOWS_
	DWORD NumberOfBytesRead;
	int totalBytesRead;

	if (h == NULL) return 0;
	totalBytesRead = 0;
	while (totalBytesRead < len) {
		// Le readfile rend la main au bout d'un timeout si pas de caractère
		// reçu.
		ReadFile(
			((_serialHandle_)h)->windowsHandle, 
			c + totalBytesRead, 
			len - totalBytesRead,
			&NumberOfBytesRead,
			NULL);
		totalBytesRead += NumberOfBytesRead;
		// Si le nombre de caractère n'a pas été reçu, on
		// attend une milliseconde avant de relance une
		// lecture. Cela donne l'occasion à un autre thread
		// de pouvoir émettre.
		if (totalBytesRead < len) {
			Sleep(1);
			if (((_serialHandle_)h)->bloque == 0) {
				// En mode non bloquant, nous venons d'attendre
				// 1 ms. Vérifions si des caractères ont été
				// reçus dans l'intervalle, auquel cas, on les
				// récupère.
				ReadFile(
					((_serialHandle_)h)->windowsHandle, 
					c + totalBytesRead, 
					len - totalBytesRead,
					&NumberOfBytesRead,
					NULL);
				totalBytesRead += NumberOfBytesRead;
				// Renvoyons le nombre de caractères reçus :
				return totalBytesRead;
			}
		}
	}

	return totalBytesRead;
#endif

#ifdef _LINUX_
	ssize_t NumberOfBytesRead;
	int totalBytesRead;

	if (h == NULL) return 0;
	totalBytesRead = 0;
	while (totalBytesRead < len) {
		NumberOfBytesRead = read(((_serialHandle_)h)->linuxHandle, (void*)(c+totalBytesRead), len-totalBytesRead);
		if (NumberOfBytesRead < 0) NumberOfBytesRead = 0;
		totalBytesRead += NumberOfBytesRead;
		if (totalBytesRead < len) {
			usleep(1000);
			if (((_serialHandle_)h)->bloque == 0) {
				NumberOfBytesRead = read(((_serialHandle_)h)->linuxHandle, (void*)(c+totalBytesRead), len-totalBytesRead);
				if (NumberOfBytesRead < 0) NumberOfBytesRead = 0;
				totalBytesRead += NumberOfBytesRead;
				return totalBytesRead;
			}
		}
	}
	return totalBytesRead;
#endif
}

/********************************************************************/

int ecriturePortSerie(portSerie h, char * c, int len) {
#ifdef _WINDOWS_
	DWORD NumberOfBytesWritten;

	if (h == NULL) return 0;
	if(
		WriteFile(
			((_serialHandle_)h)->windowsHandle, 
			(void *)c,
			len, 
			&NumberOfBytesWritten,
			NULL)
	)
		return NumberOfBytesWritten;
	else
		return 0;
#endif

#ifdef _LINUX_
	ssize_t NumberOfBytesWritten;

	if (h == NULL) return 0;
	do {
		NumberOfBytesWritten = write(((_serialHandle_)h)->linuxHandle, (void*)c, len);
		if ((NumberOfBytesWritten < 0) && (((errno==EAGAIN) || (errno==EWOULDBLOCK))))
			usleep(100);
	} while ((NumberOfBytesWritten < 0) && ((errno==EAGAIN) || (errno==EWOULDBLOCK)));
	if (NumberOfBytesWritten < 0) return 0; else return NumberOfBytesWritten;
#endif
}

/********************************************************************/
