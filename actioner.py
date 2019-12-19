import socket
import time
import turtle
import serial

from utils.better_turtle import register_koala

def start_serial(port, baudrate):
  '''
  Starts a serial communication over a USB port at a certain frequency (baudrate).
  In:
    - port (string): The USB serial port on which to send serial data (usually 'COM*').
    - baudrate (int): The baudrate at which the communiaction is listened to by the Arduino.
  Out:
    - The serial communication.
  '''
  return serial.Serial(port, baudrate)

class Actioner:
  def __init__(self, debug = False):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.action = ''
    
    # Only used to display the action on the Tkinter window
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
    '''
    Performs the current action on the Arduino and the graphical turtle.
    Resets it afterwards.
    WARNING: The amount at which the turtle spins (20) / goes forward (5) was obtained through trial and error. Change at your own risk.
    '''
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
      text_color = 'green'
      text = 'Going forward'
      ser.write(b'F')
    elif self.action == 'None':
      text_color = 'black'
      text = ''
      ser.write(b'N')

    if self.action != self.last_action:
      # Updates the graphical action display
      canvas.delete('current_action')
      canvas.create_text(-20, - 300, fill = text_color, font = 'Arial 20 italic bold', text = text, justify = 'center', tags = 'current_action')
    if self.debug:  
      print('I just performed {}'.format(self.action))

    self.last_action = self.action
    self.action = ''

  def run(self):

    # Fancy start sequence for the Arduino
    ser.write(b'L')
    time.sleep(0.25)
    ser.write(b'F')
    time.sleep(0.25)
    ser.write(b'R')
    time.sleep(0.25)
    ser.write(b'N')

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

# Please specify the right USB port and baudrate on which your Arduino is listening.
ARDUINO_PORT = 'COM7'
ARDUINO_BAUDRATE = 9600
ser = start_serial(ARDUINO_PORT, ARDUINO_BAUDRATE)

# Starts the turtle Tkinter interface with a custom 'koala' turtle.
register_koala()
turtle.penup()
turtle.shape('koala')
canvas = turtle.getcanvas()

actioner = Actioner()