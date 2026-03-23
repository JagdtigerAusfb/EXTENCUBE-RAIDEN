## Description

This files contain the code for all software required to run the robot. The code is divided in four main files: `main.py`, where the main code along with the UI elements and logic is. `kociemba.py` and `m2op.py` contain the code for the solving algothirms of the cube. And finally, `arduino.ino` contains the code for the arduino. Note that the code is not automatically writen in the arduino, you must do that manualy.

The main code can be found int the CUBE_APP folder. When running the code you should see the window:

<img width="1258" height="815" alt="image" src="https://github.com/user-attachments/assets/c4e82f1e-5489-4e53-abb8-3a05e5fa0e03" />

### Required Software
* **Arduino IDE** (or similar IDE for Arduinos)
* **Python 3.x**
* **Microsoft Visual Studio +14**

### Python Libraries
The following libraries are required for this code:

* `opencv-python`
* `PyQt6`
* `numpy`
* `kociemba`
* `pyserial`

## To run

Ensure you have manually uploaded the `.ino` file to your Arduino before starting the application. Then, run the main Python script.

