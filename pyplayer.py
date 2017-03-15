#!/usr/bin/env python
import os 
import sys
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import argparse
import pygame, time
import eyed3
import RPi.GPIO as GPIO
from time import sleep
 
user = os.getuid()
if user != 0:
	print ("Please run script as root")
	sys.exit()

WHITE = 1
BLACK = 0
MUSIC_ENDED=100
BTN1_SW3 = 20
BTN2_SW5 = 26
BTN4_SW2 = 16
SIZE = 16

pygame.mixer.music.set_endevent(MUSIC_ENDED)

def processEvent(self, event):
	if event.type == MUSIC_ENDED:
		playing=0
		pygame.mixer.music.fadeout(5)
		return None
	else:
		return event

class MusicPlayer:
	currentFile = ""
	filenames = []
	currentIndex = 0
	driver = None

	def __init__(self, videoDriver):
		self.driver = videoDriver
	def eventloop(self):
		while(True):
			if GPIO.input(BTN1_SW3) == False:
 				self.driver.write_text("THREE", SIZE)
			if GPIO.input(BTN2_SW5) == False:
				self.driver.write_text("FIVE", SIZE)
 			if GPIO.input(BTN4_SW2) == False:
				self.driver.write_text("TWO", SIZE)
			#sleep(0.1)
			if pygame.mixer.music.get_busy() == False:
				if self.currentIndex < len(self.filenames):
					self.next()
				else:
					print("Finished")
					break
			continue
		#if self.currentIndex < len(self.filenames):
			#self.next()			
		print("Finished!")
		
	def play(self):
		self.currentFile=self.filenames[self.currentIndex]
		pygame.mixer.music.load(self.currentFile)
		audiofile = eyed3.load(self.currentFile)
		self.driver.write_text(audiofile.tag.title + ', ' + audiofile.tag.artist + ', ' + audiofile.tag.album, 20)
		pygame.mixer.music.play(0)

	def next(self):
		self.currentIndex += 1
		self.play()
		
	def index(self):
		count = 0
		self.driver.write_text("Indexing...", 16)
		for folder, subs, files in os.walk("/home/pi/Music"):
			for filename in files:
				musicFile = os.path.join(folder, filename)
				self.filenames.append(musicFile)
				print(musicFile)
				count += 1
		self.driver.write_text("%d files indexed!" % count, 20)

class Driver():		
	papirus = Papirus()
	def write_text(self, text, size):
		# initially set all white background
		image = Image.new('1', self.papirus.size, WHITE)
		# prepare for drawing
		draw = ImageDraw.Draw(image)
		font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', size)
		# Calculate the max number of char to fit on line
		line_size = (self.papirus.width / (size*0.65))
		current_line = 0
		text_lines = [""]
		# Compute each line
		for word in text.split():
			# If there is space on line add the word to it
			if (len(text_lines[current_line]) + len(word)) < line_size:
				text_lines[current_line] += " " + word
			else:
				# No space left on line so move to next one
				text_lines.append("")
				current_line += 1
				text_lines[current_line] += " " + word
		current_line = 0
		for l in text_lines:
			current_line += 1
			draw.text( (0, ((size*current_line)-size)) , l, font=font, fill=BLACK)
		self.papirus.display(image)
		self.papirus.update()

def main():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(BTN1_SW3, GPIO.IN)
	GPIO.setup(BTN2_SW5, GPIO.IN)
	GPIO.setup(BTN4_SW2, GPIO.IN)
	pygame.init()
	driver = Driver()
	mPlayer = MusicPlayer(driver)
	mPlayer.index()
	mPlayer.play()
	mPlayer.eventloop()

if __name__ == '__main__':
	main()

