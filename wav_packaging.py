import subprocess
from asyncio import sleep
import wave
from utils.init import config, deviceId, logger
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

def lock_count(alarm_lock):
    if alarm_lock == 0:
        return 0
    else:
        alarm_lock = alarm_lock - 1
        return alarm_lock

async def process(filename, alarm_lock):
    res = await send_wav(filename)
    if res is not None:
        if res.headers.get('content-type') != 'application/json':
             # contentent-type is not json but status 200 when the server is not work properly
            logger.warning('Send audio - %s'%res)
            return lock_count(alarm_lock)
        else:
            event_res = await res.json()
            if (event_res['result'] == 'scream'):
                logger.info('Scream Detected!')
                if alarm_lock == 0: # if alarm is not running
                    baseUrl = config['smartbell']['alarm_url']
                    # Light the LED
                    subprocess.Popen(['python3', 'utils/pixels.py', 'alarm_light'])
                    # Send Event to the Web server
                    async with aiohttp.ClientSession() as session:
                        try:
                            await session.post('%s/%s'%(baseUrl,deviceId), json={'type':'scream'})
                        except Exception as e:
                            logger.warning('Send Scream Event - %s'%e)
                    # Play the alarm sound
                    subprocess.Popen(['aplay', '-D', 'plughw:1,0', '-d', config['smartbell']['alarm_duration'] ,
                            config['smartbell']['alarm_wav']])
                    # Lock the alarm for alarm_duration.
                    # Alarm itself makes scream event now, so we need to add sending_record_seconds
                    alarm_lock = int(config['smartbell']['alarm_duration']) + config['files']['sending_record_seconds']
                    return alarm_lock
                else:
                    return lock_count(alarm_lock)
            else:
                return lock_count(alarm_lock)
    else:
        logger.warning('Send audio result is None - maybe network error')
        return lock_count(alarm_lock)
            

if __name__ == '__main__':
    filename = 'sound/00e02dbc40cc-19.wav'
    res = send_wav(filename)

