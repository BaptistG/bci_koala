from collections import deque
import socket
import time
import numpy.random as rd
from threading import Thread

from utils.helpers import apply_filter, get_filter_coefs, puissance, votes

class BufferingThread(Thread):
  def __init__(self, streamer_socket, shared_buffer, terminator_signal):
    super(BufferingThread, self).__init__()
    self.streamer_socket = streamer_socket
    self.buffer = shared_buffer
    self.terminator_signal = terminator_signal

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

    # Read data until transmission is over
    while True:
      data = self.streamer_socket.recv(1024).decode('utf-8')

      received_buffer = ''
      if 'Recording over' in data:
        print('', 'Streaming finished')
        self.terminator_signal[0] = True
        return False
      if start_signal in data:

        received_buffer += data
        while end_signal not in received_buffer:
          data = self.streamer_socket.recv(1024).decode('utf-8')
          received_buffer += data
        try:
          received_buffer = received_buffer.split(start_signal)[-1].split(end_signal)[0]
          received_buffer = received_buffer.split(',')
          self.buffer.extend([float(value) for value in received_buffer])
        except:
          print('Error: {}'.format(self.buffer))
        return True

  def run(self):
    while not self.terminator_signal[0]:
      self.get_buffer_from_streamer()
    return

class ComputingThread(Thread):
  def __init__(self, client_connection, shared_buffer, terminator_signal):
    super(ComputingThread, self).__init__()

    self.last_start_time = time.time()
    self.buffer = shared_buffer
    self.computed_points = 0
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

    self.client_connection = client_connection
    self.action = 'None'
    self.terminator_signal = terminator_signal


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

    self.action = 'None'

  def compute(self):
    if not self.buffer:
      return

    value = self.buffer.popleft()
    for freq in self.puissances.keys():

      self.filtres[freq].append(apply_filter(value,
        self.filtres[freq][-1],
        self.filtres[freq][-2],
        freq,
        self.coefs))

      self.puissances[freq].append(puissance(self.filtres[freq][-1],
        self.puissances[freq][-1]))
    self.computed_points += 1

    if self.computed_points == 64:
      self.computed_points = 0
      self.action = votes(self.puissances)
      self.wait_for_actioner()
      self.send_action()
      self.last_start_time = time.time()

  def wait_for_actioner(self):
    '''
    Waits for the actioner to send the 'Actioner ready' message.
    WARNING: The message specified here must match the one that the actioner is programmed to send.

    Returns:
      Nothing (prints only).
    '''

    while not self.terminator_signal[0]:
      msg = self.client_connection.recv(1024).decode('utf-8')
      if not msg:
        return
      if 'Actioner ready' in msg:
        return

  def run(self):
    while not self.terminator_signal[0]:
      self.compute()
    self.client_connection.sendall(b'Actions over')
    return

class Analyzer:
  '''
  Transforms buffers of samples from a BCI signal into actions served via a socket to the Actioner.
  '''
  def __init__(self, host = 'localhost', port = 2001, buffer_size = 64, mode = 'streamer', debug = False):
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

    # Creates the streamer client socket
    self.streamer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    self.shared_buffer = deque([], buffer_size)

    self.mode = mode
    self.debug = debug

    # Use an array, so that it's shared
    self.terminator_signal = [False]

    self.buffering_thread = BufferingThread(self.streamer_socket, self.shared_buffer, self.terminator_signal)

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
    
    self.computing_thread = ComputingThread(self.client_connection, self.shared_buffer, self.terminator_signal)

    self.buffering_thread.start()
    self.computing_thread.start()

    self.buffering_thread.join()
    self.computing_thread.join()

    self.die()


  def die(self):
    '''
    Closes the client (streamer) and the server sockets.

    Returns:
      Nothing.
    '''

    self.streamer_socket.close()
    self.actioner_socket.close()

analyzer = Analyzer(buffer_size = 64)