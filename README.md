# MCSR AutoRecord

MCSR AutoRecord automatically starts recording in OBS when a Minecraft Speedrunning Ranked match begins and stops recording when the match ends. It can then rename the recording using the player's seed and match time.

## Requirements

- Windows
- OBS Studio
- OBS WebSocket enabled in OBS
- A Minecraft log file from Prism Launcher
- A Prism Launcher instance that runs MCSR Ranked

The OBS recording folder must match the path used by the program.

## Executable

A prebuilt Windows executable is available at [`output/MCSR-AutoRecord.exe`](https://github.com/dinotnt-lab/MCSR-AutoRecord/releases/tag/v1.0.0).

The executable creates a configuration file at:

```text
%APPDATA%\mcsrrecorder-dinotnt_\config.txt
```

If the configuration file does not exist, run the executable once to create it. Fill in the log file path, OBS recording folder, OBS WebSocket settings, and your Minecraft username, then restart the executable.

The `DELETE_SEED_CHANGED` setting controls whether recordings are deleted when a seed change vote affects the match.

## Run from source

Requires Python 3.

```powershell
py -m pip install -r requirements.txt
py main.py
```

Before running from source, update the configuration constants at the top of [`main.py`](main.py):

- `LOG`: path to `minecraft/logs/latest.log`
- `OBS_OUTPUT_PATH`: folder where OBS saves recordings
- `OBS_WEBSOCKET_HOST`: OBS WebSocket host
- `OBS_WEBSOCKET_PORT`: OBS WebSocket port
- `OBS_PASSWORD`: OBS WebSocket password, if one is configured
- `IGN`: your Minecraft username
- `DELETE_SEED_CHANGED`: whether to delete recordings for seed-changed matches

DISCLOSURE: This readme was made with ai as the version i made was awful, but nothing else was
