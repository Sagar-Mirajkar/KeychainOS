"""Wi-Fi scanning, touch setup, profiles, and NTP-ready connectivity."""
import json, network, os, time
PATH='/data/system/wifi_profiles.json'
def radio():
 wlan=network.WLAN(network.STA_IF); wlan.active(True); return wlan
def scan():
 result=[]
 for row in radio().scan():
  try: name=row[0].decode()
  except Exception: name=str(row[0])
  if name and name not in result: result.append(name)
 return sorted(result)
def connect(ssid,password,timeout=30):
 wlan=radio(); wlan.disconnect(); wlan.connect(ssid,password); start=time.ticks_ms()
 while not wlan.isconnected():
  if time.ticks_diff(time.ticks_ms(),start)>timeout*1000: return False
  time.sleep_ms(250)
 return True
def load_profiles():
 try:
  with open(PATH) as f: return json.load(f)
 except Exception: return {"schema":1,"profiles":[],"auto_connect":True}
def save_profile(ssid,password):
 data=load_profiles(); profiles=[p for p in data.get('profiles',[]) if p.get('ssid')!=ssid]
 profiles.append({"ssid":ssid,"password":password,"auto_connect":True}); data['profiles']=profiles
 with open(PATH+'.new','w') as f: json.dump(data,f)
 try: os.remove(PATH)
 except OSError: pass
 os.rename(PATH+'.new',PATH)
def auto_connect():
 wlan=radio()
 if wlan.isconnected(): return True
 for p in reversed(load_profiles().get('profiles',[])):
  if p.get('auto_connect',True) and connect(p.get('ssid',''),p.get('password',''),12): return True
 return False
def setup_touch(display,touch,ui,keyboard):
 names=scan()
 if not names: return False
 selected=0
 while True:
  ui.draw_grid(display,[{"name":n} for n in names],selected,'Wi-Fi',True)
  g=touch.capture_gesture()
  if g['type']=='LEFT': selected=(selected+1)%len(names)
  elif g['type']=='RIGHT': selected=(selected-1)%len(names)
  elif g['type']=='TAP':
   idx=ui.item_at(g['x'],g['y'],names,selected)
   if idx is not None:
    password=keyboard.input_password(display,touch,'Wi-Fi Password')
    if password is not None and connect(names[idx],password): save_profile(names[idx],password); return True
   elif ui.is_back_tap(g['x'],g['y']): return False
