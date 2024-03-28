import configparser
import os, subprocess
from utils.setLogger import Logger
from time import time

def print_settings(config, deviceId):
    for i in ['audio', 'files', 'smartbell']:
        print('----------'+i+'----------')
        for j in config[i]:
            print(j,':',config[i][j])
        print('')
    print('--------------------------------')
    print('Device ID:', deviceId)
    print('--------------------------------')


p_config = configparser.ConfigParser()
if os.path.exists('/boot/bssoft/smartbell_config.txt'):
    p_config.read('/boot/bssoft/smartbell_config.txt')
else:
    p_config.read('config.ini') 

if os.path.exists('/boot/bssoft/id.txt'):
    deviceId = open('/boot/bssoft/id.txt', 'r').read()
else:
    deviceId = int(time())
    open('id.txt', 'w').write(str(deviceId))
    subprocess.Popen('sudo cp id.txt /boot/bssoft/', shell=True)

# Change config strings to int
config = {s:dict(p_config.items(s)) for s in p_config.sections()}
config['audio']['chunk'] = int(config['audio']['chunk'])
config['audio']['channels'] = int(config['audio']['channels'])
config['audio']['rate'] = int(config['audio']['rate'])
config['files']['sending_record_seconds'] = int(config['files']['sending_record_seconds'])
config['smartbell']['heartbeat_interval'] = int(config['smartbell']['heartbeat_interval'])

# Set logger
logger = Logger(name='smartbell', logdir=config['files']['log_dir'], level=config['files']['log_level'])

