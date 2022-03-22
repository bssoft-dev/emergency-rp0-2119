import configparser
import subprocess
import os

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

# Calc num_sending_bundle
config['files']['num_sending_bundle'] = config['files']['sending_record_seconds']//config['audio']['record_seconds']
# Print Every settings
for i in p_config.sections():
    print('--------'+i+'--------')
    for j in config[i]:
        print(j,':',config[i][j])
    print('')
print('-------------------')

# Obtain mac_address
addr = subprocess.Popen(('ip','address'), stdout=subprocess.PIPE)
res_text = addr.stdout.read(-1).decode('utf-8')
res_ether = [i for i in res_text.split('\n') if 'ether' in i]
mac = res_ether[-1].split(' ')[5].replace(':','')


print('MAC ADDRESS:',mac)