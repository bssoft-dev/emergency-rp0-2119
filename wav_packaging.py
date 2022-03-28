import sys, subprocess, os
from pathlib import Path
import wave, pyaudio
import _thread
from utils.init import config, mac, logger
from utils.reqUtil import requests_retry_session
from time import sleep, time

import requests, json

def makeWavFile(filename, audioSampleSize, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(config['audio']['channels'])
    wf.setsampwidth(audioSampleSize)
    wf.setframerate(config['audio']['rate'])
    wf.writeframes(b''.join(frames))
    wf.close()

def send_wav(filename):
    with open(filename, 'rb') as sf:
        try: # Send the wave file to the ML server
            # res = requests.post(config['files']['send_url'], files={'file': sf}, timeout=(3,5))
            tic = time()
            res = requests_retry_session(retries=0).post(config['files']['send_url'], files={'file': sf}, timeout=(3,6))
            logger.info('Time taken: %s'%(time()-tic))
            # print(filename.split('/')[-1], res.text)
            return res
        except Exception as e:
            logger.warning('Send audio - %s'%e)
            return None

def process(filename, audioSampleSize, frames):
    makeWavFile(filename, audioSampleSize, frames)
    res = send_wav(filename)
    if res is not None:
        if res.status_code != 200:
            logger.warning('Send audio - %s'%res)
        elif (res.json()['result'] == 'scream'):
            # if another thread is running, wait for it to finish by using lock.alarm file
            if os.path.exists('lock.alarm'):
                return
            else:
                Path('lock.alarm').touch()
                baseUrl = config['smartbell']['alarm_url']
                logger.info('Scream Detected!')
                subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
                try: # Send Event to the Web server
                    requests.post('%s/%s'%(baseUrl,mac), json={'type':'scream'}, timeout=(3,5))
                except Exception as e:
                    logger.warning('Send Scream Event - %s'%e)
                subprocess.call(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                        config['smartbell']['alarm_wav']])
                os.remove('lock.alarm')

if __name__ == '__main__':
    filename = 'sound/00e02dbc40cc-19.wav'
    res = send_wav(filename)

