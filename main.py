import pyaudio, alsaaudio
import _thread
import os
from time import sleep

import requests
from utils.pixels import welcome_light
from utils.init import config, mac
import wav_packaging

def recording(stream):
    frames = []
    # Append Audio Stream for the Targeted Recording Time
    for i in range(0, int(config['audio']['rate'] / config['audio']['chunk'] * config['audio']['record_seconds'])):
        data = stream.read(config['audio']['chunk']) # Read Audio Stream with Targeted Chunk Bytes
        frames.append(data)
    return frames

def heartbeat(mac):
    while True:
        res = requests.get('{}/{}/heartbeat'.format(config['device']['heartbeat_url'], mac))
        if res.status_code != 200:
            print('Heartbeat Error')
        sleep(int(config['device']['heartbeat_interval']))

if __name__ == '__main__':
    # Initialize the directory
    os.makedirs(config['files']['sound_dir'], exist_ok=True)
    # Set Alarm Volume
    m = alsaaudio.Mixer(control='Playback', cardindex=1)
    m.setvolume(int(config['device']['volume'])) # Set the volume to 70%.
    # current_volume = m.getvolume() # Get the current Volume
    # Welcome Light
    _thread.start_new_thread(welcome_light, ())
    # Initialize the PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                channels=config['audio']['channels'],
                rate=config['audio']['rate'],
                input=True,
                frames_per_buffer=config['audio']['chunk'])
    nfile = 0
    isSend = False

    _thread.start_new_thread(heartbeat, (mac,))

    # Main Loop
    while(True):
        if nfile == config['files']['num_sending_bundle']-1:
            isSend = True
        # Record sound with duration of config['audio']['record_seconds']
        record = recording(stream)
        # Aggregate num_sending_bundle files, and send it to the ml server
        _thread.start_new_thread(wav_packaging.process, (nfile, p, record, isSend)) 
        nfile = nfile + 1
        if nfile == config['files']['num_save'] :
            nfile = 0

    stream.stop_stream()
    stream.close()
    p.terminate()
