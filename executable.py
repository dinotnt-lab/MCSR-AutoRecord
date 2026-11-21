import time
import os
import obsws_python as obs
import requests
import datetime
import configparser

root = os.getenv('APPDATA')
folder = os.path.join(root, 'mcsrrecorder-dinotnt_')
config = os.path.join(folder, 'config.txt')

defaults = {
    'Paths': {
        'LOG': r'{instance path}\logs\latest.log',
        'OBS_OUTPUT_PATH': r''
    },
    'OBS WEBSOCKET': {
        'HOST': 'localhost',
        'PORT': '4455',
        'PASSWORD': ''
    },
    'Player': {
        'IGN': ''
    },
    'Settings': {
        'DELETE_SEED_CHANGED': 'false'
    }
}

if not os.path.exists(config):
    print('creating default config')
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_dict(defaults)

    with open(config, 'w') as f:
        parser.write(f)

    print('config created -> ' + config)
    print('-'*10)
    print('FILL CONFIG WITH SETTINGS. ALL MUST BE FILLED EXCEPT OBS PASSWORD')
    print('-'*10)
    input('press enter to open config...')
    os.startfile(config)
    input('enter to continue...')
else:
    print('found config -> ' + config)

parser = configparser.ConfigParser(interpolation=None)

try:
    parser.read(config)

    LOG = parser.get('Paths', 'LOG')
    OBS_OUTPUT_PATH = parser.get('Paths', 'OBS_OUTPUT_PATH')

    OBS_WEBSOCKET_HOST = parser.get('OBS WEBSOCKET', 'HOST')
    OBS_WEBSOCKET_PORT = parser.getint('OBS WEBSOCKET', 'PORT')
    OBS_PASSWORD = parser.get('OBS WEBSOCKET', 'PASSWORD')

    IGN = parser.get('Player', 'IGN')

    DELETE_SEED_CHANGED = parser.getboolean(
        'Settings', 'DELETE_SEED_CHANGED'
    )

except (configparser.Error, ValueError) as e:
    print(f'config error: {e}')
    input('press enter to open config...')
    os.startfile(config)
    input('enter to close...')
    exit()

errors = []

if not os.path.isfile(LOG):
    errors.append(f'Log file does not exist: {LOG}')

if not os.path.isdir(OBS_OUTPUT_PATH):
    errors.append(f'OBS output folder does not exist: {OBS_OUTPUT_PATH}')

if not OBS_WEBSOCKET_HOST:
    errors.append('OBS host cannot be empty')

if not 1 <= OBS_WEBSOCKET_PORT <= 65535:
    errors.append('OBS port must be between 1 and 65535')

if not IGN:
    errors.append('Minecraft username cannot be empty')

if errors:
    print()
    print('Configuration errors:')
    for error in errors:
        print(f' - {error}')

    input('press enter to open config...')
    os.startfile(config)
    input('press enter to exit...')
    exit()

print('configuration loaded successfully')

print('connecting to obs')
try:
    obs_client = obs.ReqClient(host=OBS_WEBSOCKET_HOST, port=OBS_WEBSOCKET_PORT, password=OBS_PASSWORD)
    print('connected')
except Exception as e:
    print('OBS CONNECTION ERROR:')
    print(e)
    input('resolve errors then restart. enter to close...')
    exit()

just_reset = False
match_start = False
just_seed_changed = False
OBS_OUTPUT_FORMATS = [
    "flv",
    "mp4",
    "mkv",
    "mov",
    "ts",
    "m3u8",
    "hybrid_mp4"
]

def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def wait_for_file_release(path):
    start = time.time()
    while time.time() - start < 10.0:
        try:
            os.rename(path, path)
            return True
        except PermissionError:
            time.sleep(0.2)
    return False

logfile = open(LOG, "r")
loglines = follow(logfile)
print('minecraft log found and monitoring. system ready')
for line in loglines:
    if "resetting the server" in line:
        just_reset = True

    if "creating new queue" in line and not just_reset:
        print('match start')
        match_start = True
        obs_client.start_record()

    if "Everyone has agreed to the seed change vote. A new world will be created in 5 seconds." in line:
        just_seed_changed = True

    if "Shutdown all servers" in line and match_start:
        print('match end')
        just_reset = False
        match_start = False
        obs_client.stop_record()
        files = [f for f in os.listdir(OBS_OUTPUT_PATH) if f.endswith(tuple(OBS_OUTPUT_FORMATS))]
        latest_file = max(
            files,
            key=lambda f: os.path.getctime(os.path.join(OBS_OUTPUT_PATH, f))
        )

        if not just_seed_changed:
            resp = requests.get(f"https://api.mcsrranked.com/users/{IGN}/matches?count=1")
            seed, t = resp.json()['data'][0]['seed']['overworld'], resp.json()['data'][0]['result']['time'] if not resp.json()['data'][0]['forfeited'] else "forfeit"
        else:
            seed, t = "seed_changed", "X"
            just_seed_changed = False

        wait_for_file_release(os.path.join(OBS_OUTPUT_PATH, latest_file))
        if DELETE_SEED_CHANGED and seed == 'seed_changed':
            os.remove(os.path.join(OBS_OUTPUT_PATH, latest_file))
        else:
            os.rename(
                os.path.join(OBS_OUTPUT_PATH, latest_file),
                os.path.join(OBS_OUTPUT_PATH, f"{seed}_{t}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{latest_file.split('.')[-1]}")
            )