# Duncan Stannard, Landon Brown, Kyrel Silva
# ECET 261

# import libraries
import os
import pygame #https://www.pygame.org/docs/ref/joystick.html#pygame.joystick.init
import pigpio #http://abyz.me.uk/rpi/pigpio/python.html#set_PWM_frequency
import pprint #used for a good looking printout
import time
audio = ['/home/duncansPi/Desktop/dank.mp3','/home/duncansPi/Desktop/tokyo.mp3','/home/duncansPi/Desktop/screech.mp3','/home/duncansPi/Desktop/motorstart.mp3']
#set GPIO pins to drive outputs
FWD_Moto = 17 
RV_Moto = 27
left = 16
right = 20
#PWM_Servo_out = 
PWM_MOTO_Out = 24
# Turbo = 13
# underglow = 15
#battery_in = 29
#setup for pi gpio, due to changing default host, host name was defined
pi = pigpio.pi('duncans',8888)
#set output mode
pi.set_mode(FWD_Moto, pigpio.OUTPUT)
pi.set_mode(RV_Moto, pigpio.OUTPUT)
pi.set_mode(PWM_MOTO_Out, pigpio.OUTPUT)
pi.set_mode(left, pigpio.OUTPUT)
pi.set_mode(right, pigpio.OUTPUT)
# pi.set_mode(Turbo, pigpio.OUTPUT)
# pi.set_mode(underglow,pigpio.OUTPUT)

current_time = time.time()
		
class Motor(object):
	# class variables
	global current_time
	audionum = 0
	now_audio = 0.0
	now_speed = 0.0
	fwd = False
	rvr = False
	boost = False
	speed = 1
	sound = False
	lis = [] # moved list up here due to issue with how python passes lists between classes
	axis = []
	topemhat = "(0,0)"
	def init(self):
		pi.set_PWM_range(PWM_MOTO_Out, 100) #defines the range of the PWM output between 0 - 100
		pi.set_PWM_frequency(PWM_MOTO_Out,8000) # set frequency of the PWM to 8kHz
		pi.set_PWM_dutycycle(PWM_MOTO_Out,0) # PWM off
		pi.write(FWD_Moto,0) # fwd moto off
		pi.write(RV_Moto,0) # rev moto off
		
	def MotorOff(self): # turns motor fully off in emergency 
		pi.write(FWD_Moto,0)
		pi.write(RV_Moto,0)
		pi.write(right,0) # turn right off
		pi.write(left,0) # turn left off
		#pi.write(Turbo,0)
		self.fwd = False
		self.rvr = False

	def assign_vals(self): # assigns and outputs values passed from the controller class to the motor variables
		if(self.lis[0] == 1): # check if the X button is pressed
			fwd = True 
			#pprint.pprint(fwd) 
			pi.write(RV_Moto,0) # reverse motor pin is low
			pi.write(FWD_Moto,1) # fwd motor pin is high
			pi.set_PWM_dutycycle(PWM_MOTO_Out,10*self.speed) # set the PWM's duty cycle
		elif(self.lis[3] == 1): # check if Square button is pressed
			self.rvr == True
			pi.write(FWD_Moto,0) # fwd pin lo
			pi.write(RV_Moto,1) # rvr pin hi
			pi.set_PWM_dutycycle(PWM_MOTO_Out,10*self.speed) # set speed
			#pprint.pprint(rvr)
			
		elif(self.lis[0] == 0 and self.rvr == False): # check if x is released
			#fwd = False
			#pprint.pprint(fwd)
			pi.write(FWD_Moto,0) #turn fwd pin low
			pi.set_PWM_dutycycle(PWM_MOTO_Out,0) # set PWM duty cycle to 0
		
		elif(self.lis[3] == 0): # turn off reverse
			rvr = False
			#pprint.pprint(rvr)
			pi.set_PWM_dutycycle(PWM_MOTO_Out,0)
			
		if(self.lis[1] == 1 and (time.time()-self.now_audio) > 1):
			pygame.mixer.music.load(audio[self.audionum])
			pygame.mixer.music.play(0)
			self.now_audio = time.time()
			self.audionum = self.audionum + 1
			if (self.audionum  > 3):
				self.audionum = 0
		
		if(self.topemhat.strip()[1] == "-"):
			pi.write(right,0) # turn right off
			pi.write(left,1) # turn left on
			pprint.pprint(self.topemhat.strip()[1])
		elif(self.topemhat.strip()[1] == "1"):
			pi.write(right,1) # turn right off
			pi.write(left,0) # turn left on
			pprint.pprint(self.topemhat.strip()[1])
		elif(self.topemhat.strip()[1] == "0"):
			pi.write(right,0) # turn right off
			pi.write(left,0) # turn left on
			#pprint.pprint(self.topemhat.strip()[1])
			
		if(self.topemhat.strip()[-2] == "1" and self.topemhat.strip()[-3] != "-" and (time.time() - self.now_speed) > 1): # check the value of the hat
			if( self.speed == 8): # increase speed
				return
			else:
				self.speed += 1
				pprint.pprint(self.speed)
				pprint.pprint(self.topemhat.strip()[-2])
				self.now_speed = time.time()
		elif(self.topemhat.strip()[-2] == "1" and self.topemhat.strip()[-3] == "-"and (time.time() - self.now_speed) > 1): # check value of the hat
			if( self.speed == 1): # decrease speed
				return
			else:
				self.speed -= 1
				pprint.pprint(self.speed)
				pprint.pprint(self.topemhat.strip()[-3])
				self.now_speed = time.time()
		

# controller class holds the inits and other
class controller(object): # setup for ps4
	
	#internal variables
	moto = Motor() # allow controller class to access moto class
	controller_id = None # none as it will be set in init
	con = False
	
	def init(self): # init function for setting up the controller_id and setting length of sets in the motor class
		pygame.init() # init pygame
		con = pygame.joystick.get_count()
		pygame.joystick.init() #init pygame's joystick finds all
		while(con != 1):
			pprint.pprint("Please attach a controller")
			pygame.quit()
			pygame.init()
			pygame.joystick.init()
			con = pygame.joystick.get_count()
			
		self.controller_id = pygame.joystick.Joystick(0) # specifies only 1 joystick
		pprint.pprint(pygame.joystick.get_count())
		self.controller_id.init() #init joystick
		# setup length of sets to hold all the values
		self.moto.lis = []*self.controller_id.get_numbuttons() 
		self.moto.axis = []*self.controller_id.get_numaxes()
		# fill the sets with the values of each controller part
		
		for i in range( self.controller_id.get_numaxes()):
			self.moto.axis.append(self.controller_id.get_axis(i))
		
		for i in range(self.controller_id.get_numbuttons()):
			self.moto.lis.append(self.controller_id.get_button(i))
		
			
	def listen(self): # listen for events
		if(pygame.joystick.get_count() == 0):
			moto.motoroff()
		else:
			
			for event in pygame.event.get():
				if event.type == pygame.JOYBUTTONDOWN: # checks if any button has been pushed
						#set the position of the button in the set to the value given by the get_button function
						self.moto.lis[event.button] =self.controller_id.get_button(event.button)
						pprint.pprint(self.moto.lis)
						
				elif event.type == pygame.JOYBUTTONUP: # checks if any button has been released
						#set the position of the button in the set to the value given by the get_button function
						self.moto.lis[event.button] = self.controller_id.get_button(event.button)
						pprint.pprint(self.moto.lis)
						
				#elif event.type == pygame.JOYAXISMOTION:#returns the current position of the axis
						## set the position of the axis in the set to the value returned from get_axis function
						#self.moto.axis[event.axis] = self.controller_id.get_axis(event.axis)
						##pprint.pprint(self.moto.axis[0])
						
				elif event.type == pygame.JOYHATMOTION: # returns any change in the dpad 
						# set the value of the hat (x,y) range of -1,0,1
						self.moto.topemhat = str(self.controller_id.get_hat(event.hat))
						#pprint.pprint(self.moto.topemhat.strip()[1])
				self.moto.assign_vals() # run the assignvalues in the motor class
					
				

		
while True: # while loop
	con = controller() # set the controller class to con
	mot = Motor() # set the motor class to mot
	mot.init() # start the motor init
	con.init() # start the controller init
	pygame.mixer.music.load(audio[3])
	pygame.mixer.music.play(0)
	while True:
		con.listen()# start controller listen
	
