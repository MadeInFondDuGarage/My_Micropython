import json

_FILE = "settings.json"

_defaults = {
    "font_size": 16,
    "font_name": "default",
    "brightness": 100,
    "last_book": None,
    "last_position": 0,
    "wifi_ssid": "",
    "wifi_pass": "",
    "ftp_user": "esp32",
    "ftp_pass": "esp32",
    "refresh_mode": "full",   # full / partial
}

_data = {}

def load():
    global _data
    try:
        with open(_FILE, "r") as f:
            stored = json.load(f)
        _data = dict(_defaults)
        _data.update(stored)
    except:
        _data = dict(_defaults)

def save():
    with open(_FILE, "w") as f:
        json.dump(_data, f)

def get(key):
    return _data.get(key, _defaults.get(key))

def set(key, value):
    _data[key] = value

def reset():
    global _data
    _data = dict(_defaults)
    save()

load()
