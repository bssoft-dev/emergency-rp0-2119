import configparser
import subprocess
import os
from utils.setLogger import Logger

def print_settings(config, mac):
    for i in ['audio', 'files', 'smartbell']:
        print('----------'+i+'----------')
        for j in config[i]:
            print(j,':',config[i][j])
        print('')
    print('--------------------------------')
    print('MAC ADDRESS:',mac)
    print('--------------------------------')


p_config = configparser.ConfigParser()
if os.path.exists('/boot/smartbell_config.txt'):
    p_config.read('/boot/smartbell_config.txt')
else:
    p_config.read('config.ini') 

# Change config strings to int
config = {s:dict(p_config.items(s)) for s in p_config.sections()}
config['audio']['chunk'] = int(config['audio']['chunk'])
config['audio']['channels'] = int(config['audio']['channels'])
config['audio']['rate'] = int(config['audio']['rate'])
config['audio']['record_seconds'] = int(config['audio']['record_seconds'])
config['files']['num_save'] = int(config['files']['num_save'])
config['files']['sending_record_seconds'] = int(config['files']['sending_record_seconds'])
config['smartbell']['heartbeat_interval'] = int(config['smartbell']['heartbeat_interval'])
# config['smartbell']['alarm_duration'] = int(config['smartbell']['alarm_duration'])

# Calculate number of frames for one single chunk
config['audio']['num_frame'] = int(config['audio']['rate'] / config['audio']['chunk'] * config['audio']['record_seconds'])
# Calculate number of chunks for one single file
config['files']['num_sending_bundle'] = int(config['files']['sending_record_seconds']//config['audio']['record_seconds'])

# Obtain mac_address
#addr = subprocess.Popen(('ip','address'), stdout=subprocess.PIPE)
#res_text = addr.stdout.read(-1).decode('utf-8')
#res_ether = [i for i in res_text.split('\n') if 'ether' in i]
#mac = res_ether[-1].split(' ')[5].replace(':','')
mac = 'kkkkaaaa'


# Set logger
logger = Logger(name='smartbell', logdir=config['files']['log_dir'], level=config['files']['log_level'])

