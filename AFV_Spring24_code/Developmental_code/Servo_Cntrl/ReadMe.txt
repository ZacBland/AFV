#AFV Servo Connection Map
	
	Right brushless motor:servo 0
	Left brushless motor: servo 1
	Steering Servo: servo 2
	# Servo 3 is empty #
	Turret Base: Servo 4
	Turret Arm: Servo 5
	FLIR Base: Servo 6
	FLIR Body: Servo 7


Below are the Developmental Servo files and a description of how they work
These files are located at "/home/pi" on the raspberry pi 


ExpoThread.py
#Description: Moves chosen servo, sounds siren, triggers lights simultaneously
#input: servo_index, servo_angle
#example run script: python ExpoThread.py 4 90

LoopExpo.py
Description:Servos 4-7 iterate through ranges of movement while lights are triggered
input:none
#WARNING
#ONCE RAN, PROGRAM CAN ONLY BE STOPPED BY A kILL PROCESS
#copy this line and past in terminal: ps aux | grep Loo
# write this in terminal and replace with your "PID": kill <PID>
#text file for instructions are on destop of FLIR Beelink "How to Kill LoopExpo.txt"

relay.py
input:None
Output:Iterates through 3 relays (20,21,26) for 5sec each sounding siren, lights, and pump if connected
#example run script: python relay.py


SilentExpoThread.py
#Description Silently moves chosen servo to chosen agle, while triggering lights
#Input: servo_index, servo angle


stop.py
#Description: Sends servos 4-7 to 90 (home)
#input: None

uni.py
#Description: Combines the commands of servo 6 and servo 7 to then have servo 4 and 5 follow.
#input(prompt): servo 6 angle, servo 7 angle
#exmaple script: python uni.py
#example script: Enter angles for servo 6 and 7 (comma-separated):90,90
