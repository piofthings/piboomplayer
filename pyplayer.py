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
from gpiozero import Button
from time import sleep
 
user = os.getuid()
if user != 0:
	print ("Please run script as root")
	sys.exit()

WHITE = 1
BLACK = 0
SIZE = 16
MODE_PLAY = 100
MODE_SELECT = 101
MODE_UPDATE = 102

#pygame.mixer.music.set_endevent(MUSIC_ENDED)

class MusicPlayer:
	currentFile = ""
	filenames = []
	currentIndex = 0
	driver = None
	currentVol = 1
	mode = MODE_PLAY
	button2 = Button(16)
	button5 = Button(26)
	button3 = Button(20)

	def __init__(self, videoDriver):
		self.driver = videoDriver
		self.button5.when_pressed = self.button5Pressed
		self.button3.when_pressed = self.button3Pressed
		self.button2.when_pressed = self.button2Pressed

	def button5Pressed(self, button):
		if self.mode == MODE_PLAY:
			self.mode = MODE_SELECT
			print("Pause")
			self.pause()
		else:
			if self.mode == MODE_SELECT:
				print("Resume")
				self.resume()
			else:
				if self.mode == MODE_UPDATE:
					self.stop()
					self.play()
	
	def button3Pressed(self, button):
		if self.mode == MODE_PLAY:
			self.increaseVolume()
		else: 
			if self.mode == MODE_SELECT:
				self.next()
				self.updateDisplay(self.filenames[self.currentIndex])
				self.mode = MODE_UPDATE
		
	def button2Pressed(self, button):
		if self.mode == MODE_PLAY:
			self.decreaseVolume()
		else:
			if self.mode == MODE_SELECT:
				self.previous()
				self.updateDisplay(self.filenames[self.currentIndex])
				self.mode = MODE_UPDATE
	
	def eventloop(self):
		while(True):
			if pygame.mixer.music.get_busy() == False:
				if self.currentIndex < len(self.filenames):
					self.playNext()
					self.updateDisplay(self.filenames[self.currentIndex])
				else:
					print("Finished")
					break
			sleep(0.05)
			continue
		print("Finished!")

	def pause(self):
		pygame.mixer.music.pause()

	def resume(self):
		pygame.mixer.music.unpause()
		self.mode = MODE_PLAY

	def stop(self):
		pygame.mixer.music.stop()

	def increaseVolume(self):
		currVol = pygame.mixer.music.get_volume()
		if currVol < 1.0:
			newVol = currVol + 0.01
			pygame.mixer.music.set_volume(newVol)
			print("Volume = %f" % newVol)

	def decreaseVolume(self):
		currVol = pygame.mixer.music.get_volume()
		if currVol > 0:
			newVol = currVol - 0.01
			pygame.mixer.music.set_volume(newVol)
			print("Volume = %f" % newVol)

	def play(self):
		self.currentFile=self.filenames[self.currentIndex]
		pygame.mixer.music.load(self.currentFile)
		pygame.mixer.music.play(0)
		self.mode = MODE_PLAY

	def next(self):
		if self.currentIndex < len(self.filenames):
			self.currentIndex += 1
		else:
			self.currentIndex = 0

	def playNext(self):
		self.next()
		self.play()
	
	def previous(self):
		if self.currentIndex > 0:
			self.currentIndex -= 1
		else:
			self.currentIndex = len(self.filenames) - 1

	def playPrevious(self):
		self.previous()
		self.play()

	def updateDisplay(self, filename):
		audiofile = eyed3.load(filename)
		self.driver.write_text(audiofile.tag.title + ', ' + audiofile.tag.artist + ', ' + audiofile.tag.album, 14)
		

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
	pygame.init()
	driver = Driver()
	mPlayer = MusicPlayer(driver)
	mPlayer.index()
	mPlayer.play()
	mPlayer.updateDisplay(mPlayer.currentFile)
	mPlayer.eventloop()

if __name__ == '__main__':
	main()

