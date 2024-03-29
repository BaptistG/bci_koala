# bci_koala

Mini projet: a brain-controlled robot.

## The principle
3 parts so far:

### A BCI listener/streamer
**Neural signals** to guide the robots are captured here. They fall into one of those 4 categories:
  - Turn left
  - Turn right
  - Go forward
  - Do nothing (default)
  
Those signals are direct neural electric signals captured by electrodes on a man's head.
Signals are grouped into fixed-length buffers and sent to the next layer:

### A frequency analyzer
Once a satisfactory sample has been recorded, it's sent to an analyzer layer. This layer must determine the action that is being ordered by the man.
Each action corresponds to a signal with a certain defined **frequency** (they actually come from staring at flashing lights).
The analyzer thus conducts a frequency analysis of the given sample and then decides what action to send to the next layer:

### A robot (or close to one)
The robot is given an **order** and must then execute it. For now, we'll do with a robot's simulation and an Arduino Serial communication.

## Dependencies/requirements

This project was made using Python 3.6: please make sure to install the interpreter before running the code.
3 non-standard libraries were used: to install them, simply run `pip install -r ./requirements.txt` from the source folder.

You are given 2 options for running the code: either on a single machine or on different ones. In the latter case, please be sure to specify the right IP addresses of your machines when interconnecting the different components (`localhost` by default).

## The code
3 main Python scripts should be detailed:

### The Streamer
`streamer.py` parses a `.txt` recording and sends it to an analyzer via a **socket**.

*How to start:*
`python streamer.py`

### The Analyzer
`analyzer.py` parses the buffers received from the *Streamer* and analyzes them. It then sends an action to an actioner via another **socket**.
It uses functions from `helpers.py`, located in the *utils* folder.

*How to start:*
1) Start the *Streamer*
2) `python -i analyzer.py`
3) `analyzer.connect()`
4) `analyzer.run()`

### The Actioner
`actioner.py` parses the actions received from the *Analyzer* and executes them. So far it uses **turtle** to mock the robot and sends serial communications to an **Arduino** board.

*How to start:*
1) Start the *Analyzer*
2) `python -i actioner.py`
3) `actioner.connect()`
4) `actioner.run()`

## Bonuses

### Docstring
Docstring is available for those 3 modules, just use `help(ClassName)` to get info on any of those classes (doc coming soon).

### Arduino
The Actioner sends signals over a specified Serial USB port (`COM7` by default) at a certain BaudRate (`9600`by default), expecting to reach an **Arduino** board programmed to read those signals.
Such a code is provided in the *arduino* folder: this code can be televersed on an **Arduino Uno** board using the **Arduino IDE** and matching the following schematics for pin-outs:

![alt text](./images/arduino_schematics.png "Arduino schematics")
