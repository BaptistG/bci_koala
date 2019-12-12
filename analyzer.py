from collections import deque
import socket
import time
import numpy.random as rd
from threading import Thread

from helpers import apply_filter, get_filter_coefs, puissance, vote_action

class Analyzer:
  '''
  Transforms buffers of samples from a BCI signal into actions served via a socket to the Actioner.
  '''
  def __init__(self, host = 'localhost', port = 2001, buffer_size = 128, mode = 'streamer', debug = False):
    '''
    In:
      - host (string): The hostname/IP of the analyzer server ('localhost' by default).
      - port (int): The analyzer server port number (2001 by default).
      - buffer_size (int): The size the buffer must reach before sending the action to the actioner.
      - debug (bool): True means every step will be printed out. False only prints minimal info.
    WARNING: The host and port specified must match the ones given to the Actioner object when connecting it to the analyzer.

    Returns:
      The Analyzer object.
    '''

    # Creates the analyzer server socket
    self.actioner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.actioner_socket.bind((host, port))

    self.action = ''
    self.buffering_thread = Thread()

    self.computing_thread = Thread()

    # Creates the streamer client socket
    self.streamer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.buffer = []

    self.puissances = {
        7.5: deque([0], 64),
        11: deque([0], 64),
        13.5: deque([0], 64)
    }

    self.filtres = {
        7.5: deque([0, 0], 2),
        11: deque([0, 0], 2),
        13.5: deque([0, 0], 2)
    }

    self.coefs = get_filter_coefs([7.5, 11, 13.5])

    self.mode = mode
    self.debug = debug

  def run_buffering_thread(self):
    streamer.recv()
    buffer.append()

  def run_computing_thread(self):
    if len(buffer()) > 0:
        for freq in self.puissances.keys():

            self.filtres[freq].append(apply_filter(value,
                self.filtres[freq][-1],
                self.filtres[freq][-2],
                freq,
                self.coefs))

            self.puissances[freq].append(puissance(self.filtres[freq][-1],
                self.puissances[freq][-1]))

    if time.now() - self.start_time >= 0.25:
        self.action = vote_action(self.puissances)
        self.start_time = time.now()
        self.send_action()


  def connect(self, streamer_host = 'localhost', streamer_port = 2000):
    '''
    Connects the streamer client socket to the streamer server socket.
    In:
      - streamer_host (string): The hostname/IP at which the streamer server is running ('localhost' by default).
      - streamer_port (int): The port number at which the streamer server is running (2000 by default).
    WARNING: Those default values match the default values specified in the Streamer class. If you change them, make sure you change the other ones accordingly.

    Returns:
      Nothing (prints only).
    '''

    self.streamer_socket.connect((streamer_host, streamer_port))
    print('Analyzer connected to streamer')

  def wait_for_actioner(self):
    '''
    Waits for the actioner to send the 'Actioner ready' message.
    WARNING: The message specified here must match the one that the actioner is programmed to send.

    Returns:
      Nothing (prints only).
    '''

    if self.debug:
      print('Waiting for actioner...')
    while True:
      msg = self.client_connection.recv(1024).decode('utf-8')
      if not msg:
        return
      if 'Actioner ready' in msg:
        if self.debug:
          print('Ready message received')
        return

  def get_buffer_from_streamer(self):
    '''
    1) Sends the 'Analyzer ready' flag.
    2) Receives a buffer from the streamer server socket and then appends it to the local buffer.
       The transmission starts and ends with delimiter messages from the server.
    WARNINGS:
      - The method assumes that the connection with the streamer has already been established (will crash otherwise).
      - The delimiters must match the ones specified to the streamer in the method responsible for sending the buffer.

    Returns:
      False: The streamer has read all the data: the connection is over.
      True: There are still more buffers to come: keep the connection alive.
    '''

    # Start flag
    start_signal = 'Sending buffer'

    # End flag
    end_signal = 'Buffer sent'

    # Warn streamer that analyzer is ready to receive data
    self.streamer_socket.sendall(b'Analyzer ready')

    if self.debug:
      print('Ready message sent')

    # Read data until transmission is over
    while True:
      data = self.streamer_socket.recv(1024).decode('utf-8')
      if self.debug:
        print(data)

      received_buffer = ''
      if 'Recording over' in data:
        print('', 'Streaming finished')
        self.die()
        return False
      if start_signal in data:
        if self.debug:
          print('Receiving buffer')
        received_buffer += data
        while end_signal not in received_buffer:
          data = self.streamer_socket.recv(1024).decode('utf-8')
          received_buffer += data
        if self.debug:
          print('Buffer received')
        try:
          received_buffer = received_buffer.split(start_signal)[-1].split(end_signal)[0]
          received_buffer = received_buffer.split(',')
          self.buffer += [float(value) for value in received_buffer]
        except:
          print('Error: {}'.format(self.buffer))
        return True

  def compute_action(self):
    '''
    Inspects the buffer and computes the action to send to the actioner.
    Empties the buffer afterwards, so it's ready to receive more data.

    Returns:
      Nothing (prints only).
    '''

    self.buffer.compute_action()

  def send_action(self):
    '''
    Sends the action to the clients of the analyzer socket and then empties it.
    The transmission starts and ends with delimiter messages.
    WARNINGS:
      - The method assumes that the connection with the actioner has already been established (will crash otherwise).
      - The delimiters must match the ones specified to the actioner in the method responsible for parsing the action.

    Returns:
      Nothing (prints only).
    '''

    # Start flag
    self.client_connection.sendall(b'Sending actions')

    self.client_connection.sendall(self.action.encode('utf-8'))

    # End flag
    self.client_connection.sendall(b'Actions sent')

    if self.debug:
      print('Actions sent')
    self.action = ''

  def run(self):
    '''
    Main method.
    Does the following:
      1) Starts the server socket.
      2) Waits for the actioner client socket to start a connection.
      3) Until the connection with the streamer is ended:
        - Wait until the actioner is ready.
        - while the buffer is not full.
          - Send the 'Analyzer ready' flag to the streamer.
          - Receives a buffer from the streamer.
        - When the buffer is full, analyzes it and computes the corresponding action.
        - Sends it to the actioner.
      5) Alerts the actioner when the streamer connection is over.
      6) Closes the server socket (a.k.a.: 'dies').

    WARNING: Make sure that the 'finished' message sent matches the one specified to the actioner's parser.

    Returns:
      Nothing (prints only)
    '''

    self.actioner_socket.listen(1)
    print('Analyzer listening...')
    conn, addr = self.actioner_socket.accept()
    print('Analyzer connected by ', addr)
    self.client_connection = conn
    start_time = time.start()
    while True:
      self.wait_for_actioner()
      while len(self.buffer) < self.buffer_size:
        if not self.get_buffer_from_streamer():
          self.client_connection.sendall(b'Actions over')
          self.die()
          return
      while not self.compute_action():


      self.send_action()


  def die(self):
    '''
    Closes the client (streamer) and the server sockets.

    Returns:
      Nothing.
    '''

    self.streamer_socket.close()
    self.actioner_socket.close()

analyzer = Analyzer(buffer_size = 128)
