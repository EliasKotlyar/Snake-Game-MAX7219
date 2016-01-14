#!/usr/bin/env python
# ---------------------------------------------------------
# Filename: snake.py
# ---------------------------------------------------------
# snake Game for using with MAX7219 Matrices
#
# v1.0
# F.Stern 2014
# ---------------------------------------------------------
# You need to copy the files of this repository to this folder
# https://github.com/tutRPi/multilineMAX7219
# multilineMAX7219.py and multilineMAX7219_fonts.py
#
# The RPi.GPIO library has to be installed, if joypad is used
# https://pypi.python.org/pypi/RPi.GPIO
# ---------------------------------------------------------
#
# run as root with:
# sudo python snake.py
#
# If you use a joypad, set USE_JOYPAD = True and make sure the
# GPIO Pins are correct
# You also have to adjust your Matrix width and height in multilineMAX7219.py
# ---------------------------------------------------------


from Point import Point


from random import randrange
import threading, sys
import time


# Directions
DIR_U = Point(0,1)
DIR_D = Point(0,-1)
DIR_R = Point(1,0)
DIR_L = Point(-1,0)

# Make sure you set these correct in multilineMAX7219.py
WIDTH = 30
HEIGHT = 30

tail = [Point(WIDTH//2, HEIGHT//2)]
start = randrange(2)
direction = Point(start, 1 - start)	# init direction

target = Point()
running = True			# loop variable
speed = 0.1				# getting faster, the longer the snake is
wasDisplayed = True		# to allow only one new direction per frame

import opc, time
client = opc.Client('192.168.0.183:7890')
pixels = [ (0,0,0) ] * WIDTH*HEIGHT

def getPixelNum(x,y):
	if(y%2==0):
		x=WIDTH-x-1

	pixelNum=(y-1)*WIDTH*-1+x
	return pixelNum
#LEDMatrix.init()
def setPixel(x,y,toggle=False,sleep = 0.01):	
	if(toggle==True):
		color = (255, 255, 255)
	else:
		color = (0,0,0)
	setColorPixel(x,y,color,sleep)
	
	
def setColorPixel(x,y,color,sleep = 0.01):
	global pixels
	i = getPixelNum(x,y)
	pixels[i] = color			
	time.sleep(sleep)	

def setAll(toggle):
	global pixels
	if toggle:
		pixels = [ (255,255,255) ] * WIDTH*HEIGHT		
	else:
		pixels = [ (0,0,0) ] * WIDTH*HEIGHT		
	render()	
		
def render():
	global pixels
	client.put_pixels(pixels)

def display():
	global pixels
	# displays all on the LED Matrices
	#LEDMatrix.gfx_set_all(GFX_OFF)
	pixels = [ (0,0,0) ] * WIDTH*HEIGHT

	for p in tail:
		setPixel(int(p.x), int(p.y), True)

	setColorPixel(int(target.x), int(target.y), (255,0,0))
	render()
	

	global wasDisplayed
	wasDisplayed = True

def setTarget():
	# sets a new target, which is not in the tail of the snake
	global target
	target = Point(randrange(WIDTH+1), randrange(HEIGHT+1))
	while target in tail:
		target = Point(randrange(WIDTH+1), randrange(HEIGHT+1))

def move():
	global running, speed
	if running:
		newPosition = tail[0] + direction
		if newPosition.x > WIDTH:
			newPosition.x -= WIDTH+1
		elif newPosition.x < 0:
			newPosition.x += WIDTH+1
		if newPosition.y > HEIGHT:
			newPosition.y -= HEIGHT+1
		elif newPosition.y < 0:
			newPosition.y += HEIGHT+1
		
		if newPosition == target:
			tail.insert(0,newPosition)
			setTarget()
			speed = max(0.07, min(0.3, 2/float(len(tail))))
		elif newPosition not in tail:
			tail.insert(0, newPosition)
			tail.pop()
		else:
			# Game Over
			running = False
			for i in range(3):
				setAll(True);				
				time.sleep(0.3)
				setAll(False);				
			print "Game Over. Press any Key to exit. Score: " + str(len(tail)-1)
			#LEDMatrix.clear_all()
			raise SystemExit("\n")
		
		# threading for calling it every period
		threading.Timer(speed, move).start ()
	else:
		#LEDMatrix.clear_all()
		pass

	display()

	
def changeDirection(newDirection = direction):
	global direction, wasDisplayed
	if wasDisplayed:
		if newDirection != direction and (newDirection.x != -direction.x or newDirection.y != -direction.y):
			direction = newDirection
			wasDisplayed = False
	
	

if __name__ == "__main__":
	
	setTarget()
	move()

	# Use Keyboard Arrows
	from _Getch import _Getch
	getch = _Getch()
	print "To end the game press <q>"
	while running:
		try:
			key = ord(getch())
			if key == 27: #ESC
				key = ord(getch())
				if key == 91:
					key = ord(getch())
					if key == 65: #Up arrow
						changeDirection(DIR_U)
						#setPixel(0,1,True)
					if key == 66: #Down arrow
						changeDirection(DIR_D)
						#setPixel(0,1,False)
					elif key == 67: #right arrow
						changeDirection(DIR_R)
						#setPixel(29,29,True)
					elif key == 68: #left arrow
						#setPixel(29,29,False)
						changeDirection(DIR_L)

			elif key == 113:
				setAll(False)
				print "Goodbye"
				running = False
				break
		except KeyboardInterrupt:
			setAll(False)
			print "\nGoodbye"
