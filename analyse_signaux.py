import matplotlib.pyplot as plt
import threading
import socket

F_EQ = 256
T_WINDOW = 1
HOST = ''	
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
s.listen(10)
print('Socket now listening')

def send(buff):
    on_receive(buff)
    print('sent')

def on_receive(buff):
    print('ok')

with open('./enonce/acquisition_biosemi/Enregistrements/herve001.txt', 'r') as record_trame:
    records = record_trame.readlines()
    rec_list_stereo = [r.split(' ')[:2] for r in records]
    rec_list_means = [(float(r[0]) + float(r[1])) / 2 for r in rec_list_stereo]
    N_ECH_WINDOW = F_EQ * T_WINDOW
    buffer = []
    for r in rec_list_means:
        buffer.append(r)
        if len(buffer) == N_ECH_WINDOW:
#            send(buffer)
            buffer = []