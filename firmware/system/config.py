"""Atomic JSON configuration storage."""
import json, os
PATH='/data/system/config.json'
DEFAULTS={"schema":1,"theme":"epaper_minimal","timezone_minutes":330,"time_format":24,"screen_timeout_seconds":60,"screensaver":"clock","image_mode":"fit"}
def load():
 try:
  with open(PATH) as f: data=json.load(f)
  result=dict(DEFAULTS); result.update(data); return result
 except Exception: return dict(DEFAULTS)
def save(data):
 temp=PATH+'.new'
 with open(temp,'w') as f: json.dump(data,f)
 try: os.remove(PATH)
 except OSError: pass
 os.rename(temp,PATH)
def get(key,default=None): return load().get(key,default)
def set(key,value):
 data=load(); data[key]=value; save(data); return value
