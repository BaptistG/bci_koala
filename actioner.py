import socket
import time
import turtle
import serial

ARDUINO_PORT = 'COM7'
ARDUINO_BAUDRATE = 9600
ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUDRATE)

turtle.penup()
turtle.shape('turtle')

class Actioner:
  def __init__(self, debug = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.actions = ''
    self.debug = debug

  def connect(self, analyzer_host = 'localhost', analyzer_port = 2001):
    self.socket.connect((analyzer_host, analyzer_port))
    print('Actioner connected to analyzer')

  def get_actions_from_analyzer(self):
    start_signal = 'Sending actions'
    end_signal = 'Actions sent'
    if self.debug:
      print('Waiting for analyzer')
    while True:
      data = self.socket.recv(1024).decode('utf-8')
      if 'Actions over' in data:
        print('', 'Analysis finished')
        self.die()
        return False
      if start_signal in data:
        self.actions += data
        if self.debug:
          print('Receiving action...')
        while end_signal not in self.actions:
          data = self.socket.recv(1024).decode('utf-8')
          self.actions += data
        if self.debug:
          print('Actions received')
        try:
          self.actions = self.actions.split(start_signal)[-1].split(end_signal)[0]
        except:
          print('Error: {}'.format(self.actions))
        return True

  def perform_actions(self):
    if self.actions == 'TurnRight':
      turtle.right(45)
      ser.write(b'R')
    elif self.actions == 'TurnLeft':
      turtle.left(45)
      ser.write(b'L')
    elif self.actions == 'Forward':
      turtle.forward(20)
      ser.write(b'F')
    elif self.actions == 'None':
      ser.write(b'N')
    print('I just performed {}'.format(self.actions))
    self.actions = ''

  def run(self):
    ser.write(b'L')
    time.sleep(0.25)
    ser.write(b'F')
    time.sleep(0.25)
    ser.write(b'R')
    time.sleep(0.25)
    ser.write(b'N')

    self.connect()
    while True:
      self.socket.sendall(b'Actioner ready')
      if self.debug:
        print('Ready message sent')
      if self.get_actions_from_analyzer():
        self.perform_actions()
      else:
        return

  def die(self):
    self.socket.close()

actioner = Actioner()