import socket
import time
import turtle
import serial

from utils.better_turtle import register_koala 

ARDUINO_PORT = 'COM7'
ARDUINO_BAUDRATE = 9600
ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUDRATE)

register_koala()
turtle.penup()
turtle.shape('koala')
canvas = turtle.getcanvas()

class Actioner:
  def __init__(self, debug = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.action = ''
    self.last_action = ''
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
        self.action += data
        if self.debug:
          print('Receiving action...')
        while end_signal not in self.action:
          data = self.socket.recv(1024).decode('utf-8')
          self.action += data
        if self.debug:
          print('Actions received')
        try:
          self.action = self.action.split(start_signal)[-1].split(end_signal)[0]
        except:
          print('Error: {}'.format(self.action))
        return True

  def perform_actions(self):
    if self.action == 'TurnRight':
      turtle.right(20)
      text_color = 'blue'
      text = 'Turning right'
      ser.write(b'R')
    elif self.action == 'TurnLeft':
      turtle.left(20)
      text_color = 'red'
      text = 'Turning left'
      ser.write(b'L')
    elif self.action == 'Forward':
      turtle.forward(5)
      text_color = 'darkgreen'
      text = 'Going forward'
      ser.write(b'F')
    elif self.action == 'None':
      text_color = 'black'
      text = ''
      ser.write(b'N')

    if self.action != self.last_action:
      canvas.delete('current_action')
      canvas.create_text(-20, - 300, fill = text_color, font = 'Arial 20 italic bold', text = text, justify = 'center', tags = 'current_action')
    print('I just performed {}'.format(self.action))
    self.last_action = self.action
    self.action = ''

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