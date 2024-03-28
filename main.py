import pyaudio, alsaaudio
import os, subprocess
import asyncio
from asyncio import sleep
import aiohttp
from queue import Queue

from utils.init import config, deviceId, print_settings, logger
from utils.alsahandle import noalsaerr
import wav_packaging

import RPi.GPIO as GPIO

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)
gRecord_frames = Queue()

def alarm_state(asyncState):
    if asyncState.alarm_lock == 0:
        return False
    else:
        return True

def lock_count(asyncState, lock=False):
# scream result by alarm sound will be ignored with this locking mechanism
    if lock:
        asyncState.alarm_lock = int(config['smartbell']['alarm_duration']) + config['files']['sending_record_seconds']
    elif asyncState.alarm_lock == 0:
        pass
    else:
        count = asyncState.alarm_lock - 1
        asyncState.alarm_lock = count

async def button_callback(asyncState):
    while True:
        state = GPIO.input(BUTTON)
        if not (state): # button is pressed
            logger.info('Button Pressed')
            baseUrl = config['smartbell']['alarm_url']
            # Play the alarm sound
            subprocess.Popen(['pkill', '-f', 'aplay'])
            await sleep(0.1)
            subprocess.Popen(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                config['smartbell']['alarm_wav']])
            # Light the LED
            subprocess.Popen(['pkill', '-f', 'light'])
            await sleep(0.1)
            subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
            # Send the alarm to the server
            async with aiohttp.ClientSession() as session:
                try:
                    await session.post('%s/%s'%(baseUrl,deviceId), json={'type':'button'})
                except Exception as e:
                    logger.warning('Send Button Event - %s'%e)
            lock_count(asyncState, lock=True)
        await sleep(0.1)

async def heartbeat():
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                await session.get('{}/{}/heartbeat'.format(config['smartbell']['heartbeat_url'], deviceId))
            except Exception as e:
                logger.warning('Heartbeat - %s'%e)
        await sleep(config['smartbell']['heartbeat_interval'])

def record_callback(in_data, frame_count, time_info, status):
    global gRecord_frames
    gRecord_frames.put(in_data)
    return (in_data, pyaudio.paContinue)    

async def audio_process(stream, asyncState):
    global gRecord_frames
    nfile = 0
    isSend = False
    count = 0
    while(True):
        try:
            logger.debug(count)
            count += 1
            if isSend:
                filename = f"{deviceId}-{nfile}.raw"
                audios = [gRecord_frames.get() for _ in range(gRecord_frames.qsize())] 
                await wav_packaging.process(b''.join(audios), filename, asyncState)
            if count == 1:
                # Record with non-blocking mode of pyaudio
                stream.start_stream()
                isSend = True
            # Record sound with duration of config['audio']['sending_record_seconds']
            await sleep(config['files']['sending_record_seconds'])
            nfile += 1
        except KeyboardInterrupt:
            stream.stop_stream()
            stream.close()
            quit()

async def coroutin_main(stream):
    # Setup an object to use like a global variable in asyncios
    asyncState = type('', (), {})()
    asyncState.alarm_lock = 0
    await asyncio.gather(heartbeat(), button_callback(asyncState), audio_process(stream, asyncState))

if __name__ == '__main__':
    # Log starting
    logger.info('##############################################')
    logger.info('BS soft Corporation. Smartbell is Started.')

    # Start Welcome Light
    subprocess.Popen(['python3', 'utils/pixels.py', 'welcome_light'])
    # Welcome Message
    print('')
    print('############################################################')
    print('Smartbell - Audio Recording and Alarm System V 1.0')
    print('############################################################')
    # Print Every settings
    print_settings(config, deviceId)

    # Initialize the directory
    os.makedirs(config['files']['sound_dir'], exist_ok=True)
        
    # Set Alarm Volume
    m = alsaaudio.Mixer(control='Playback', cardindex=1)
    m.setvolume(int(config['smartbell']['volume'])) # Set the volume to custom value
    # current_volume = m.getvolume() # Get the current Volume

    # Initialize the PyAudio
    with noalsaerr():
        p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                channels=config['audio']['channels'],
                rate=config['audio']['rate'],
                input=True,
                frames_per_buffer=config['audio']['chunk'],
                stream_callback=record_callback)
    audioSampleSize = p.get_sample_size(pyaudio.paInt16)

    # Main loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(coroutin_main(stream))
    loop.close()

