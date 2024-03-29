import subprocess
import wave
from utils.init import config, deviceId, logger
import aiohttp
from main import lock_count, alarm_state

async def send_wav(filename):
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            data = aiohttp.FormData()
            data.add_field('file',
                        open(filename, 'rb'),
                        filename=filename.split('/')[-1],
                        content_type='audio/wav')
            res = await session.post('http://api-2035.bs-soft.co.kr/v3/upload-analysis/', data=data)
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
            res = await session.post(f"{config['files']['send_url']}?threshold={config['smartbell']['detect_threshold']}", data=data)
            return res
        except Exception as e:
            logger.warning('Send audio - %s'%e)
            return None

async def process(rawSound, filename, asyncState):
    if alarm_state(asyncState):
        # Don't do anything except lock_count if alarm is on
        lock_count(asyncState)
        return
    res = await send_raw_sound(rawSound, filename)
    if res is not None:
        if res.headers.get('content-type') != 'application/json':
             # contentent-type is not json but status 200 when the server is not work properly
            logger.warning('Send audio - %s'%res)
        else:
            event_res = await res.json()
            if (event_res['result'] == 'scream'):
                logger.info('Scream Detected!')
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
                subprocess.Popen(['aplay', '-D', f'plughw:{config["smartbell"]["cardnumber"]},0', '-d', config['smartbell']['alarm_duration'] ,
                        config['smartbell']['alarm_wav']])
                # Lock the alarm for alarm_duration.
                lock_count(asyncState, lock=True)
    else:
        logger.warning('Send audio result is None - maybe network error')
            

if __name__ == '__main__':
    filename = 'sound/00e02dbc40cc-19.wav'
    res = send_wav(filename)

