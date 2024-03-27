import subprocess
import wave
from utils.init import config, deviceId, logger
import aiohttp
from main import lock_count

async def send_wav(filename):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            data = aiohttp.FormData()
            data.add_field('file',
                        open(filename, 'rb'),
                        filename=filename.split('/')[-1],
                        content_type='audio/wav')
            res = await session.post('%s?threshold=%s'%(config['files']['send_url'],
                            config['smartbell']['detect_threshold']), data=data)
            return res
        except Exception as e:
            logger.warning('Send audio - %s'%e)
            return None

async def send_raw_sound(sound, filename):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            data = aiohttp.FormData()
            data.add_field('file',
                        sound,
                        filename=filename,
                        content_type='audio/l16;rate=16000')
            res = await session.post("http://api-2106.bs-soft.co.kr/v2/smartbell/1sec-analysis/", data=data)
            return res
        except Exception as e:
            logger.warning('Send audio - %s'%e)
            return None

async def process(rawSound, filename, asyncState):
    res = await send_raw_sound(rawSound, filename)
    if res is not None:
        if res.headers.get('content-type') != 'application/json':
             # contentent-type is not json but status 200 when the server is not work properly
            logger.warning('Send audio - %s'%res)
            # return lock_count()
            lock_count(asyncState)
        else:
            event_res = await res.json()
            if (event_res['result'] == 'scream'):
                logger.info('Scream Detected!')
                if asyncState.alarm_lock == 0: # If alarm is not locked
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
                    lock_count(asyncState, lock=True)
                else:
                    lock_count(asyncState)
            else:
                lock_count(asyncState)
    else:
        logger.warning('Send audio result is None - maybe network error')
        return lock_count(asyncState)
            

if __name__ == '__main__':
    filename = 'sound/00e02dbc40cc-19.wav'
    res = send_wav(filename)

