# original URL https://github.com/larsimmisch/pyalsaaudio/blob/master/playwav.py

# Simple test script that plays (some) wav files

from __future__ import print_function

import sys
import wave
import getopt
import alsaaudio

def play(device, wavfile):	

	format = None
	# 8bit is unsigned in wav files
	if wavfile.getsampwidth() == 1:
		format = alsaaudio.PCM_FORMAT_U8
	# Otherwise we assume signed data, little endian
	elif wavfile.getsampwidth() == 2:
		format = alsaaudio.PCM_FORMAT_S16_LE
	elif wavfile.getsampwidth() == 3:
		format = alsaaudio.PCM_FORMAT_S24_3LE
	elif wavfile.getsampwidth() == 4:
		format = alsaaudio.PCM_FORMAT_S32_LE
	else:
		raise ValueError('Unsupported format')

	periodsize = wavfile.getframerate() // 8

	# print('%d channels, %d sampling rate, format %d, periodsize %d\n' 
	# 	% (wavfile.getnchannels(), wavfile.getframerate(), format, periodsize))

	device = alsaaudio.PCM(channels=wavfile.getnchannels(), rate=wavfile.getframerate(), format=format, periodsize=periodsize, device=device)
	
	data = wavfile.readframes(periodsize)
	while data:
		# Read data from stdin
		device.write(data)
		data = wavfile.readframes(periodsize)

def play_wav(wavfile):
	with wave.open(wavfile, 'rb') as f:
		play('default', f)

def usage():
	print('usage: playwav.py [-d <device>] <file>', file=sys.stderr)
	sys.exit(2)

if __name__ == '__main__':
	play_wav('../police-siren.wav')
    