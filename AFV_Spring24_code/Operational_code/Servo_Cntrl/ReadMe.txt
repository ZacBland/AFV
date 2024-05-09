#AFV Servo Connection Map
	
	Right brushless motor:servo 0
	Left brushless motor: servo 1
	Steering Servo: servo 2
	# Servo 3 is empty #
	Turret Base: Servo 4
	Turret Arm: Servo 5
	FLIR Base: Servo 6
	FLIR Body: Servo 7


Below are the Operational Servo files and a description of how they work
These files are located at "/home/pi" on the raspberry pi 
Files such as "servo3.py" are called via ssh commands from the beelink, which has the FLIR operations and data for heat source detection

AutoExpo.py
Description:Servos 4-7 iterate through ranges of movement while lights are triggered
input:none
#example run script: python AutoExp.py


servo3.py
#Description: Moves chosen servo,triggers lights simultaneously
#input: servo_index, servo_angle
#example run script: python servo3.py 4 90

stop.py
#Description: Sends servos 4-7 to 90 (home)
#input: None
#example: stop.py
