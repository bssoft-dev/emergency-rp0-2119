import pyaudio
import wave
import _thread
import requests
import json
import os
from time import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 1
FILE_CYCLE = 30
NUM_FILES_SEND = 10
SERVER_URL = 'http://api-2106.bs-soft.co.kr/v1/upload-analysis/'
SOUND_DIR = './sound'
SEND_FILE_FLAG = 'BS_TEST-'

def recording(stream):
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    return frames

def thread_process(nfile, p, frames, isSend):
    filename = f'{SOUND_DIR}/{nfile}.wav'
    sfilename = f'{SOUND_DIR}/{SEND_FILE_FLAG}{nfile}.wav'
    write_wav(filename, p, frames)
    print(nfile)
    if isSend :
        stime = time()
        # Aggregate the files' contents
        fileagg = []
        inum = FILE_CYCLE + nfile + 1
        print(inum)
        for i in range(NUM_FILES_SEND):
            with wave.open(f'{SOUND_DIR}/{(inum-NUM_FILES_SEND+i)%FILE_CYCLE}.wav', 'rb') as wavfile :
                fileagg.append([wavfile.getparams(), wavfile.readframes(wavfile.getnframes())])
        # Write the contents as one file
        with wave.open(sfilename, 'wb') as output:
            output.setparams(fileagg[0][0])
            for i in range(len(fileagg)):
                output.writeframes(fileagg[i][1])        

        # Send the aggregated single file
        send_wav(sfilename)
        etime = time()
        print(f'thread process time: {etime-stime}s')

def write_wav(filename, p, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def send_wav(filename):
    sf = open(filename, 'rb')
    stime = time()
    res = requests.post(SERVER_URL, files={'file': sf})
    etime = time()
    print(f'sending time: {etime-stime}')
    result = json.loads(res.text)
    print(result)

if __name__ == '__main__':
    if not(os.path.isdir(SOUND_DIR)):
        os.mkdir(SOUND_DIR)
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    nfile = 0
    isSend = False
    while(True):
        if nfile == NUM_FILES_SEND-1:
            isSend = True
        # Record sound with duration of RECORD_SECONDS
        record = recording(stream)
        # Aggregate NUM_FILES_SEND files, and send it
        _thread.start_new_thread(thread_process, (nfile, p, record, isSend)) 
        nfile = nfile + 1
        if nfile == FILE_CYCLE :
            nfile = 0

    stream.stop_stream()
    stream.close()
    p.terminate()
  
