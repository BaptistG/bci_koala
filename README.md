# bci_koala

Mini projet to valider l'année.

## The principle
3 parts so far:

### A BCI listener/streamer
**Neural signals** to guide the robots are captured here. They fall into one of those 4 categories:
  - Turn left
  - Turn right
  - Go forward
  - Do nothing (stop)
Those signals are direct neural electric signals captured by electrodes on a (bald) man's head.
Signals are grouped into fixed-length samples and sent to the next layer:

### A frequency analyzer
Once a satisfactory sample has been recorded, it's sent to an analyzer layer. This layer must determine the action that is being ordered by the (bald) man.
Each action corresponds to a signal with a certain defined **frequency** (they actually come from staring at a flashing light).
The analyzer thus conducts a frequency analysis of the given sample and then decides what action to send to the next layer:

### A robot (or close to one)
The robot is given an **order** and must then executes it. For now, we'll do with a robot's simulation (but stay tuned).

## The code
So far, 3 Python scripts:

### The Streamer
`streamer.py` parses a `.txt` recording and sends it to an analyzer via a **socket**.

*How to start:*
`python streamer.py`

### The Analyzer
`analyzer.py` parses the buffers received from the *Streamer* and analyzes them. It then sends an action to an actioner via another **socket**.

*How to start:*
1) Start the *Streamer*
2) `python -i analyzer.py`
3) `analyzer.connect()`
4) `analyzer.run()`

### The Actioner
`actioner.py` parses the actions received from the *Analyzer* and executes them. So far it uses **turtle** to mock the robot.

*How to start:*
1) Start the *Analyzer*
2) `python -i actioner.py`
3) `actioner.connect()`
4) `actioner.run()`