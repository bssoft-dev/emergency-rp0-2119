import pyaudio, alsaaudio
import _thread
import os, subprocess
import asyncio
from asyncio import sleep
import aiohttp

from utils.init import config, mac, print_settings, logger
from utils.alsahandle import noalsaerr
import wav_packaging

import RPi.GPIO as GPIO

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)
nBundle = config['files']['num_sending_bundle']
num_record_frames = config['audio']['num_frame']*nBundle
gRecord_frames = [b'']*num_record_frames # Initialize num_record_frames length empty byte array

async def button_callback(mac):
    while True:
        state = GPIO.input(BUTTON)
        if not (state): # button is pressed
            logger.info('Button Pressed')
            baseUrl = config['smartbell']['alarm_url']
            # Turn on the LED
            subprocess.Popen(['pkill', '-f', 'light'])
            await sleep(0.1)
            subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
            # Send the alarm to the server
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post('%s/%s'%(baseUrl,mac), json={'type':'button'})
                except Exception as e:
                    logger.warning('Send Button Event - %s'%e)
            # Play the alarm sound
            subprocess.Popen(['pkill', '-f', 'aplay'])
            await sleep(0.1)
            subprocess.Popen(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                config['smartbell']['alarm_wav']])
        await sleep(0.1)

async def heartbeat(mac):
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                await session.get('{}/{}/heartbeat'.format(config['smartbell']['heartbeat_url'], mac))
            except Exception as e:
                logger.warning('Heartbeat - %s'%e)
        await sleep(config['smartbell']['heartbeat_interval'])

def record_callback(in_data, frame_count, time_info, status):
    gRecord_frames.append(in_data)
    del gRecord_frames[0]
    return (in_data, pyaudio.paContinue)    

async def audio_process(stream):
    # Main Loop
    nfile = 0
    isSend = False
    logger.info('Record Loop is Started, Recording and Sending')
    count = 0
    while(True):
        try:
            logger.debug(count)
            count += 1
            if (isSend==False) and (nfile == nBundle-1):
                isSend = True
            # Record sound with duration of config['audio']['record_seconds']
            # try:
            stream.start_stream()
            await sleep(config['audio']['record_seconds'])
            stream.stop_stream()
            # except Exception as e:
            #     logger.warning('Recording Error: %s'%e)
            #     exit() 
            if isSend:
                filename = '%s/%s-%d.wav'%(config['files']['sound_dir'], mac, nfile)
                await wav_packaging.process(filename, audioSampleSize, gRecord_frames)
            nfile += 1
            if nfile == config['files']['num_save'] :
                nfile = 0
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            quit()

async def coroutin_main(stream, mac):
    await asyncio.gather(heartbeat(mac), button_callback(mac), audio_process(stream))

if __name__ == '__main__':
    # Log starting
    logger.info('##############################################')
    logger.info('Smartbell is Started. Enjoy your safety.')

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
                start=False,
                frames_per_buffer=config['audio']['chunk'],
                stream_callback=record_callback)
    audioSampleSize = p.get_sample_size(pyaudio.paInt16)

    # Main loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutin_main(stream,mac))
    loop.close()

