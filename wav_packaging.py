import subprocess, os
from pathlib import Path
import wave
from utils.init import config, mac, logger
import aiohttp


def makeWavFile(filename, audioSampleSize, frames):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(config['audio']['channels'])
    wf.setsampwidth(audioSampleSize)
    wf.setframerate(config['audio']['rate'])
    wf.writeframes(b''.join(frames))
    wf.close()

async def send_wav(filename):
    # async with aiofiles.open(filename, 'rb') as sf:
        # Send the wave file to the ML server
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            data = aiohttp.FormData()
            data.add_field('file',
                        open(filename, 'rb'),
                        filename=filename.split('/')[-1],
                        content_type='audio/wav')
            res = await session.post(config['files']['send_url'], data=data)
            return res
        except Exception as e:
            logger.warning('Send audio - %s'%e)
            return None

async def process(filename, audioSampleSize, frames):
    makeWavFile(filename, audioSampleSize, frames)
    res = await send_wav(filename)
    if res is not None:
        if res.headers.get('content-type') != 'application/json':
            logger.warning('Send audio - %s'%res)
        else:
            event_res = await res.json()
            if (event_res['result'] == 'scream') and not os.path.exists('lock.alarm'):
                # if another thread is running, wait for it to finish by using lock.alarm file
                Path('lock.alarm').touch()
                baseUrl = config['smartbell']['alarm_url']
                logger.info('Scream Detected!')
                subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
                # Send Event to the Web server
                async with aiohttp.ClientSession() as session:
                    try:
                        await session.post('%s/%s'%(baseUrl,mac), json={'type':'scream'})
                    except Exception as e:
                        logger.warning('Send Scream Event - %s'%e)
                # Play the alarm sound
                subprocess.Popen(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                        config['smartbell']['alarm_wav']])
                os.remove('lock.alarm')

if __name__ == '__main__':
    filename = 'sound/00e02dbc40cc-19.wav'
    res = send_wav(filename)

