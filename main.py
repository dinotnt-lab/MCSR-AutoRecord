import time
import os
import obsws_python as obs
import requests
import datetime

LOG = r"C:\Users\Roo\AppData\Roaming\PrismLauncher\instances\mcsr\minecraft\logs\latest.log"
OBS_WEBSOCKET_HOST = "localhost"
OBS_WEBSOCKET_PORT = 4455
OBS_PASSWORD = ""
IGN = 'dinotnt_'
OBS_OUTPUT_PATH = r"D:\Videos"
DELETE_SEED_CHANGED = True

obs_client = obs.ReqClient(host=OBS_WEBSOCKET_HOST, port=OBS_WEBSOCKET_PORT, password=OBS_PASSWORD)

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

print('listening')
logfile = open(LOG, "r")
loglines = follow(logfile)
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