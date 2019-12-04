import socket
import time
import numpy.random as rd

class Analyzer:
  def __init__(self, host = 'localhost', port = 2001, debug = False):
    self.actioner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.actioner_socket.bind((host, port))
    self.action = ''

    self.streamer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.buffer = ''
    self.debug = debug

  def connect(self, streamer_host = 'localhost', streamer_port = 2000):
    self.streamer_socket.connect((streamer_host, streamer_port))
    print('Analyzer connected to streamer')

  def wait_for_actioner(self):
    if self.debug:
      print('Waiting for actioner...')
    while True:
      msg = self.client_connection.recv(1024)
      if not msg:
        return
      if 'Actioner ready' in msg:
        if self.debug:
          print('Ready message received')
        return

  def get_buffer_from_streamer(self):
    start_signal = 'Sending buffer'
    end_signal = 'Buffer sent'
    self.streamer_socket.sendall('Analyzer ready')
    if self.debug:
      print('Ready message sent')
    while True:
      data = self.streamer_socket.recv(1024)
      # print(data)
      if 'Recording over' in data:
        print('', 'Streaming finished')
        self.die()
        return False
      if start_signal in data:
        if self.debug:
          print('Receiving buffer')
        self.buffer += data
        while end_signal not in self.buffer:
          data = self.streamer_socket.recv(1024)
          self.buffer += data
        if self.debug:
          print('Buffer received')
        try:
          self.buffer = self.buffer.split(start_signal)[-1].split(end_signal)[0]
        except:
          print('Error: {}'.format(self.buffer))
        return True

  def compute_action(self):
    possible_actions = ['TurnRight', 'TurnLeft', 'Forward', 'None']
    N = len(self.buffer.split(',')) + rd.randint(4)
    self.buffer = ''
    self.action = possible_actions[N % 4]

  def transmit_action(self):
    self.client_connection.sendall('Sending actions')
    self.client_connection.sendall(self.action)
    self.client_connection.sendall('Actions sent')
    if self.debug:
      print('Actions sent')
    self.action = ''

  def run(self):
    self.actioner_socket.listen(1)
    print('Analyzer listening...')
    conn, addr = self.actioner_socket.accept()
    print('Analyzer connected by ', addr)
    self.client_connection = conn
    while True:
      self.wait_for_actioner()
      if self.get_buffer_from_streamer():
        self.compute_action()
        self.transmit_action()
      else:
        self.client_connection.sendall('Actions over')
        break

    self.die()


  def die(self):
    self.streamer_socket.close()
    self.actioner_socket.close()

analyzer = Analyzer()