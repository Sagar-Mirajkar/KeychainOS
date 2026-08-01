"""Create and repair the standard KeychainOS writable filesystem."""
import json, os
REQUIRED_DIRECTORIES = (
 "/apps/games","/apps/tools","/apps/organizer","/apps/remote","/apps/connections",
 "/apps/developer","/apps/settings","/apps/about","/themes","/data/system","/data/apps",
 "/media/images","/media/animations","/media/text","/media/documents","/media/incoming",
 "/media/originals","/media/unsupported","/media/failed","/packages/incoming",
 "/packages/installed","/packages/backups","/packages/failed","/cache/icons",
 "/cache/thumbnails","/cache/temporary","/logs/system","/logs/apps","/logs/updates",
 "/trash/apps","/trash/files","/trash/themes","/disabled/games","/disabled/tools",
 "/disabled/organizer","/disabled/remote","/disabled/connections","/disabled/developer",
 "/disabled/settings","/disabled/themes","/recovery/backups","/recovery/pending",
 "/recovery/failed","/lost+found")
CATEGORIES={"games":("Games",10),"organizer":("Organizer",20),"tools":("Tools",30),
"remote":("Remote",40),"connections":("Connections",50),"developer":("Developer",60),
"settings":("Settings",70),"about":("About",80)}
def exists(path):
 try: os.stat(path); return True
 except OSError: return False
def mkdirs(path):
 current=""
 for part in path.split('/'):
  if part:
   current += '/' + part
   if not exists(current): os.mkdir(current)
def write_json_if_missing(path,value):
 if not exists(path):
  with open(path,'w') as f: json.dump(value,f)
def ensure_structure():
 created=0
 for path in REQUIRED_DIRECTORIES:
  if not exists(path): mkdirs(path); created += 1
 for cid,(name,order) in CATEGORIES.items():
  write_json_if_missing('/apps/%s/category.json'%cid,{"format":1,"id":cid,"name":name,"order":order,"enabled":True,"icon":None})
 write_json_if_missing('/data/system/config.json',{"schema":1,"theme":"epaper_minimal","timezone_minutes":330,"time_format":24,"screen_timeout_seconds":60,"screensaver":"clock","image_mode":"fit"})
 write_json_if_missing('/data/system/wifi_profiles.json',{"schema":1,"profiles":[],"auto_connect":True})
 write_json_if_missing('/data/system/installed_packages.json',{"schema":1,"packages":[]})
 return created
