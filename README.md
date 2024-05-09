# AFV

This repository is the overall code for the Spring 2024 Autonomous Firefighting Vehicle. Contained in this repo is
several folders used for the control of the AFV.

### Setup Instructions

To install all needed packages, please run:
``pip install -r requirements.txt``

### FLIR

Code for the FLIR camera will be found under the `FLIR/` directory.

### GPS

Code for the GPS module will be found under the `GPS/` directory.

### PI

Code for the Raspberry Pi will be found under the `Pi/` directory.

### Navigation

Code for navigation will be found within the `mpc/` and `search/` folders.

The A* search algorithm will be found within the `search/a_star/` directory. `a_star.py` contains
the search and reconstruct path functions used for path planning. To see usage, see main function of `mpc/simulate.py`

`mpc/simulate.py` creates a visual simulation using the MPC class to follow a path given from A* search as closely as possible.

#### Graph GUI

The Graph GUI will allow you to create a graph network using Google Maps. This graph network will
be used for A* search to help find the optimal path from one point to another.

To run the GUI: `python ./search/GUI/gui.py`

Currently, the GUI saves to a json file located in `logs/`. To change this directory, change the save_file variable
to your location.


