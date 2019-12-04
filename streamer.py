import socket
import time
import sys

def print_progress(progress, debug, N_points = 20):
  '''
  Outputs a simple progress bar that looks like this: '====>....'.
  In:
    - progress (float): The total progress made, between 0 (start) and 1 (end)
    - debug (bool):
      True means there are outputs that shouldn't be overwritten: the bar is printed in a newline.
      False means there are no other outputs: the bar can be printed inline, using the standard output directly to overwrite itself.
    - N_points (int): The total length of the progress bar string desired.
  
  Returns:
    Nothing (prints only)
  '''

  progress = int(progress * N_points)
  progress_string = ''.join(['='] * (progress - 1)) + '>' + ''.join(['.'] * (N_points - progress))
  if debug:
    print(progress_string)
  else:
    sys.stdout.write(progress_string + "\r")
    sys.stdout.flush()

class Streamer:
  '''
  Transforms a complete recording (.txt) into a 'Stream', a flow of small buffers served via a socket to the Analyzer.
  '''
  def __init__(self, buffer_size, host = 'localhost', port = 2000, debug = False):
    '''
    In:
      - buffer_size (int): The size of the buffers (list) to be sent.
      - host (string): The hostname/IP of the streaming server ('localhost' by default).
      - port (int): The streaming server port number (2000 by default).
      - debug (bool): True means every step will be printed out. False only prints minimal info.
    WARNING: The host and port specified must match the ones given to the Analyzer object when connecting it to the streamer.

    Returns:
      The Streamer object.
    '''

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((host, port))
    self.buffer = []
    self.buffer_size = buffer_size
    self.debug = debug

  def is_buffer_full(self):
    '''
    If the buffer is full, it's ready to be sent.

    Returns:
      If the buffer is full or not (bool).
    '''

    return self.buffer_size == len(self.buffer)

  def send_buffer(self):
    '''
    Sends the buffer to the clients of the streamer socket and then empties it.
    The connection starts and ends with delimiter messages.
    WARNINGS:
      - The method assumes that the connection with the analyzer has already been established (will crash otherwise).
      - The delimiters must match the ones specified to the analyzer in the method responsible for parsing the buffer.

    Returns:
      Nothing (prints only).
    '''

    self.client_connection.sendall('Sending buffer')
    self.client_connection.sendall(','.join(self.buffer))
    self.client_connection.sendall('Buffer sent')
    if self.debug:
      print('Buffer sent')
    self.buffer = []

  def wait_for_analyzer(self):
    '''
    Waits for the analyzer to send the 'Analyzer ready' message.
    WARNING: The message specified here must match the one that the analyzer is programmed to send.

    Returns:
      Nothing (prints only).
    '''

    if self.debug:
      print('Waiting for analyzer...')
    while True:
      msg = self.client_connection.recv(1024)
      if 'Analyzer ready' in msg:
        if self.debug:
          print('Ready message received, sending buffer')
        return

  def run(self):
    '''
    Main method.
    Does the following:
      1) Starts the server socket
      2) Waits for the analyzer client socket to start a connection
      3) Reads the specified recording file lines
      4) For each line:
        - Outputs the file exploration progress (like this '=======>......')
        - Appends it to the buffer
        - Checks if the buffer is full
        - If it's full, sends it to the analyzer
      5) Alerts the analyzer when the recording has been totally read.
      6) Closes the server socket.

    WARNINGS:
      - Expected format for the recording file is: 'left_value1 right_value1 whatever\n [...] left_valuek right_valuek whatever\n'
      - Left and right values are separated by a delimiter (' | ') that must then match the one provided to the analyzer parser
      - Also make sure that the 'finished' message sent matches the one specified to the analyzer's parser.

    Returns:
      Nothing (prints only)
    '''

    self.socket.listen(1)
    print('Streamer listening...')
    conn, addr = self.socket.accept()
    print('Streamer connected by ', addr)
    self.client_connection = conn
    with open('./recording.txt', 'r') as recording:
      lines = recording.readlines()
      L = len(lines)
      i = 0.0
      for line in lines:
        i += 1
        line = ' | '.join(line.split(' ')[:2])
        self.buffer.append(line)
        if self.is_buffer_full():
          progress = i / L
          print_progress(progress, self.debug)
          self.wait_for_analyzer()
          self.send_buffer()
      self.client_connection.sendall('Recording over')
      print('', 'Reading finished')
      self.die()
      

  def die(self):
    self.socket.close()

# The file contains 256 recordings/s
F_ACQ = 256
# Analyze samples of length = 1s
T_ECH = 1 

streamer = Streamer(int(F_ACQ * T_ECH))
streamer.run()