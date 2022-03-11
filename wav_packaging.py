import requests
import json
import wave, pyaudio
from utils.init import config
from time import time

def aggregate_wav(filename, p, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(config['audio']['channels'])
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(config['audio']['rate'])
    wf.writeframes(b''.join(frames))
    wf.close()


def send_wav(filename):
    sf = open(filename, 'rb')
    stime = time()
    res = requests.post(config['files']['send_url'], files={'file': sf})
    etime = time()
    print('sending time: {}'.format(etime-stime))
    result = json.loads(res.text)
    print(result)


def process(nfile, p, frames, isSend):
    ''' 
    Aggregate/Write and Send Sound File
    '''
    filename = '{}/{}.wav'.format(config['files']['sound_dir'], nfile)
    sfilename = '{}/{}{}.wav'.format(config['files']['sound_dir'], config['files']['send_name_flag'], nfile)
    aggregate_wav(filename, p, frames)
    print(nfile)
    if isSend :
        stime = time()
        # Aggregate the files' contents
        fileagg = []
        inum = config['files']['num_save'] + nfile + 1
        print(inum)
        for i in range(config['files']['num_sending_bundle']):
            with wave.open('{}/{}.wav'.format(config['files']['sound_dir'],
                (inum - config['files']['num_sending_bundle']+i)%config['files']['num_save']),'rb') as wavfile :
                fileagg.append([wavfile.getparams(), wavfile.readframes(wavfile.getnframes())])
        # Write the contents as one file
        with wave.open(sfilename, 'wb') as output:
            output.setparams(fileagg[0][0])
            for i in range(len(fileagg)):
                output.writeframes(fileagg[i][1])        
        # Send the aggregated single file
        # send_wav(sfilename)
        etime = time()
        print('thread process time: {}s'.format(etime-stime))

