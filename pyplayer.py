import os
import sys
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import argparse
import pygame, time
import eyed3

user = os.getuid()
if user != 0:
    print ("Please run script as root")
    sys.exit()

WHITE = 1
BLACK = 0
MUSIC_ENDED=100

pygame.mixer.music.set_endevent(MUSIC_ENDED)


def processEvent(self, event):
	if event.type == MUSIC_ENDED:
		playing=0
		pygame.mixer.music.fadeout(5)
		return None
	else:
		return event

def main():
	#p = argparse.ArgumentParser()
	#p.add_argument('content', type=str)
	#p.add_argument('--fsize', '-s',type=int , default=20)
	#args = p.parse_args()
	papirus = Papirus()
	#if args.content:
	#	print("Writing to Papirus.......")
	print("Finished!")
	pygame.init()
	pygame.mixer.music.load('iwyb.mp3')
	audiofile = eyed3.load("iwyb.mp3")
	write_text(papirus, audiofile.tag.title + ', ' + audiofile.tag.artist + ', ' + audiofile.tag.album, 20)
	pygame.mixer.music.play(0)

	while(pygame.mixer.music.get_busy()):
		continue

def write_text(papirus, text, size):
	# initially set all white background
	image = Image.new('1', papirus.size, WHITE)
	# prepare for drawing
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', size)
	# Calculate the max number of char to fit on line
	line_size = (papirus.width / (size*0.65))
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
	papirus.display(image)
	papirus.update()

if __name__ == '__main__':
	main()

