"""RTC, timezone and NTP time service."""
import machine, time
try: import ntptime
except ImportError: ntptime=None
def sync():
 if ntptime is None: return False
 try: ntptime.settime(); return True
 except Exception: return False
def local_tuple(offset_minutes=330):
 return time.localtime(time.time()+int(offset_minutes)*60)
def format_time(offset_minutes=330,hour24=True):
 t=local_tuple(offset_minutes); hour=t[3]
 if hour24: return '%02d:%02d:%02d'%(hour,t[4],t[5])
 suffix='AM' if hour<12 else 'PM'; hour=hour%12 or 12
 return '%02d:%02d %s'%(hour,t[4],suffix)
def format_date(offset_minutes=330):
 t=local_tuple(offset_minutes); return '%04d-%02d-%02d'%(t[0],t[1],t[2])
