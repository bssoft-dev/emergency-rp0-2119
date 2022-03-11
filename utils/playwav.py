# original URL https://github.com/larsimmisch/pyalsaaudio/blob/master/playwav.py

# Simple test script that plays (some) wav files

from __future__ import print_function

import sys
import wave
import getopt
import alsaaudio

def play(device, file):	

	format = None

	# 8bit is unsigned in wav files
	if f.getsampwidth() == 1:
		format = alsaaudio.PCM_FORMAT_U8
	# Otherwise we assume signed data, little endian
	elif f.getsampwidth() == 2:
		format = alsaaudio.PCM_FORMAT_S16_LE
	elif f.getsampwidth() == 3:
		format = alsaaudio.PCM_FORMAT_S24_3LE
	elif f.getsampwidth() == 4:
		format = alsaaudio.PCM_FORMAT_S32_LE
	else:
		raise ValueError('Unsupported format')

	periodsize = f.getframerate() // 8

	# print('%d channels, %d sampling rate, format %d, periodsize %d\n' % (f.getnchannels(),
	# 																	 f.getframerate(),
	# 																	 format,
	# 																	 periodsize))

	device = alsaaudio.PCM(channels=f.getnchannels(), rate=f.getframerate(), format=format, periodsize=periodsize, device=device)
	
	data = f.readframes(periodsize)
	while data:
		# Read data from stdin
		device.write(data)
		data = f.readframes(periodsize)


def usage():
	print('usage: playwav.py [-d <device>] <file>', file=sys.stderr)
	sys.exit(2)

if __name__ == '__main__':
    with wave.open('../police-siren.wav', 'rb') as f:
        playwav.play('default', f)