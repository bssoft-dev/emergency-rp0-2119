import configparser
import subprocess

p_config = configparser.ConfigParser()
p_config.read('config.ini') 

# change strings to int
config = {s:dict(p_config.items(s)) for s in p_config.sections()}
config['audio']['chunk'] = int(config['audio']['chunk'])
config['audio']['channels'] = int(config['audio']['channels'])
config['audio']['rate'] = int(config['audio']['rate'])
config['audio']['record_seconds'] = int(config['audio']['record_seconds'])
config['files']['num_save'] = int(config['files']['num_save'])
config['files']['num_sending_seconds'] = int(config['files']['num_sending_seconds'])

# obtain mac_address
addr = subprocess.Popen(('ip','address'), stdout=subprocess.PIPE)
res_text = addr.stdout.read(-1).decode('utf-8')
res_ether = [i for i in res_text.split('\n') if 'ether' in i]
mac = res_ether[-1].split(' ')[5]

