import pyaudio, alsaaudio
import _thread
import os, subprocess
from time import sleep

import requests

from utils.init import config, mac, print_settings, logger
from utils.alsahandle import noalsaerr
import wav_packaging

import RPi.GPIO as GPIO

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

def button_callback(mac):
    while True:
        state = GPIO.input(BUTTON)
        if not (state): # button is pressed
            logger.info('Button Pressed')
            baseUrl = config['smartbell']['alarm_url']
            # Turn on the LED
            subprocess.Popen(['pkill', '-f', 'light'])
            sleep(0.1)
            subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
            # Send the alarm to the server
            try:
                requests.post('%s/%s'%(baseUrl,mac), json={'type':'button'}, timeout=(3,5))
            except Exception as e:
                logger.warning('Send Button Event - %s'%e)
            # Play the alarm sound
            subprocess.Popen(['pkill', '-f', 'aplay'])
            sleep(0.1)
            subprocess.Popen(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                config['smartbell']['alarm_wav']])
        sleep(0.1)

def recording(frames,stream):
    # Read Audio Stream for the Targeted Recording Time
    for i in range(len(frames)):
        frames[i] = stream.read(config['audio']['chunk']) # Read Audio Stream with Targeted Chunk Bytes
    return frames

def heartbeat(mac):
    while True:
        try:
            requests.get('{}/{}/heartbeat'.format(config['smartbell']['heartbeat_url'], mac), timeout=(1,3))
        except Exception as e:
            print('Heartbeat -',e)
        sleep(config['smartbell']['heartbeat_interval'])


if __name__ == '__main__':
    # Start Welcome Light
    subprocess.Popen(['python3', 'utils/pixels.py', 'welcome_light'])
    # Welcome Message
    print('')
    print('############################################################')
    print('Smartbell - Audio Recording and Alarm System V 1.0')
    print('############################################################')
    # Print Every settings
    print_settings(config, mac)

    # Initialize the directory
    os.makedirs(config['files']['sound_dir'], exist_ok=True)
    if os.path.exists("lock.alarm"):
        os.remove("lock.alarm")
        
    # Set Alarm Volume
    m = alsaaudio.Mixer(control='Playback', cardindex=1)
    m.setvolume(int(config['smartbell']['volume'])) # Set the volume to 70%.
    # current_volume = m.getvolume() # Get the current Volume


    # Initialize the PyAudio
    with noalsaerr():
        p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                channels=config['audio']['channels'],
                rate=config['audio']['rate'],
                input=True,
                frames_per_buffer=config['audio']['chunk'])
    audioSampleSize = p.get_sample_size(pyaudio.paInt16)

    # Start Heartbeat Thread
    _thread.start_new_thread(heartbeat, (mac,))

    # Start Button Callback Thread
    _thread.start_new_thread(button_callback, (mac,))

    # Main Loop
    nfile = 0
    isSend = False
    nFrame = int(config['audio']['rate'] / config['audio']['chunk'] * config['audio']['record_seconds'])
    nBundle = config['files']['num_sending_bundle']
    record_frames = [b'']*nFrame # Initialize nFrame length empty byte array
    send_frames = [b'']*(nFrame*nBundle) # Initialize nFrame*num_sending_bundle length empty byte array
    logger.info('##############################################')
    logger.info('Main Loop is Started, Recording and Sending')
    count = 0
    while(True):
        try:
            logger.info(count)
            count += 1
            if (isSend==False) and (nfile == nBundle-1):
                isSend = True
            # Record sound with duration of config['audio']['record_seconds']
            try:
                record_frames = recording(record_frames, stream)
            except Exception as e:
                logger.warning('Recording Error: %s'%e)
                p.terminate()
                sleep(10)
                with noalsaerr():
                    logger.info('Restarting PyAudio')
                    p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                    channels=config['audio']['channels'],
                    rate=config['audio']['rate'],
                    input=True,
                    frames_per_buffer=config['audio']['chunk'])
                # sleep(1)

            # # # Save the recorded sound
            # filename = '%s/%d.wav'%(config['files']['sound_dir'], nfile)
            # wav_packaging.makeWavFile(filename, audioSampleSize, record_frames)
            # send_frames[nfile%nBundle*nFrame:(nfile%nBundle+1)*nFrame] = record_frames
            if isSend:
                filename = '%s/%s-%d.wav'%(config['files']['sound_dir'], mac, nfile)
                _thread.start_new_thread(wav_packaging.process, (filename, audioSampleSize, send_frames) )
            nfile += 1
            if nfile == config['files']['num_save'] :
                nfile = 0
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            p.terminate()
            quit()
