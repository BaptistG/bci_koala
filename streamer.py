import socket
import time
import sys

def print_progress(progress, debug):
  N_points = 20
  progress = int(progress * N_points)
  progress_string = ''.join(['='] * (progress - 1)) + '>' + ''.join(['.'] * (N_points - progress))
  if debug:
    print(progress_string)
  else:
    sys.stdout.write(progress_string + "\r")
    sys.stdout.flush()

class Streamer:
  def __init__(self, buffer_size, host = 'localhost', port = 2000, debug = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((host, port))
    self.buffer = []
    self.buffer_size = buffer_size
    self.debug = debug

  def is_buffer_full(self):
    return self.buffer_size == len(self.buffer)

  def send_buffer(self):
    self.client_connection.sendall('Sending buffer')
    self.client_connection.sendall(','.join(self.buffer))
    self.client_connection.sendall('Buffer sent')
    if self.debug:
      print('Buffer sent')
    self.buffer = []

  def wait_for_analyzer(self):
    if self.debug:
      print('Waiting for analyzer...')
    while True:
      msg = self.client_connection.recv(1024)
      if 'Analyzer ready' in msg:
        if self.debug:
          print('Ready message received, sending buffer')
        return

  def run(self):
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

F_ACQ = 256 # 256 recordings/s
T_ECH = 1 # Analyze samples every 1s

streamer = Streamer(int(F_ACQ * T_ECH))
streamer.run()