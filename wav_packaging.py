import sys, subprocess
import wave, pyaudio
from utils.init import config
from time import time

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
        res = requests.post(config['files']['send_url'], files={'file': sf}, verify=False)
        print(res.text)

def agg_wav(nfile):
    ''' 
    Open and Aggregate Sound File
    '''
    sfilename = '{}/{}{}.wav'.format(config['files']['sound_dir'], config['files']['send_name_flag'], nfile)
    stime = time()
    # Aggregate the files' contents
    nBundle = config['files']['num_sending_bundle']
    fileagg = list(range(nBundle))
    inum = int(nfile) + 1
    for i in range(nBundle):
        with wave.open('{}/{}.wav'.format(config['files']['sound_dir'],
            (inum - nBundle + i) % config['files']['num_save'] + 1),'rb') as wavfile :
            fileagg[i] =  [wavfile.getparams(), wavfile.readframes(wavfile.getnframes())]
    # Write the contents as one file
    with wave.open(sfilename, 'wb') as output:
        output.setparams(fileagg[0][0])
        for i in range(len(fileagg)):
            output.writeframes(fileagg[i][1])        
    # Send the aggregated single file
    print('sendfile : %s'%(sfilename))
    send_wav(sfilename)
    etime = time()
    print('thread process time: %fs'%(etime-stime))

def str2list(text):
    cmd = text.replace('\'','').split()
    # 이 코드를 보시는 분 한번만 눈감아 주셈
    cmd[5] = cmd[5] + ' ' + cmd[6]
    cmd[8] = cmd[8] + ' ' + cmd[9]
    del cmd[9]
    del cmd[6]
    return cmd

def process(filename, audioSampleSize, frames):
    makeWavFile(filename, audioSampleSize, frames)
    # send_wav(filename)
    curl = "curl -X POST http://api-2106.bs-soft.co.kr/smaltBell/upload-analysis/ "
    cmdStr = curl + "-H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F file=@"+filename+";type=audio/wav"
    cmd = str2list(cmdStr)
    subprocess.Popen(cmd) # Background execution of curl command

if __name__ == '__main__':
    fname = 'sound/00e02dbc40cc-19.wav'
    curl = "curl -X POST http://api-2106.bs-soft.co.kr/smaltBell/upload-analysis/"
    cmdStr = curl + "-H 'accept: application/json' -H 'Content-Type: multipart/form-data' -F file=@"+fname+";type=audio/wav"
    cmd = str2list(cmdStr)
    print(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    print(out)
    print(err)

