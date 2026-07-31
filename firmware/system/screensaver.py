"""Clock, blank, and RGB565 image screensavers."""
import time
from system.ui import PAPER, INK, MUTED
from system import time_service
def run(display,touch,config):
 mode=config.get('screensaver','clock') if isinstance(config,dict) else 'clock'
 if mode=='blank': display.fill(0x0000); display.backlight_off()
 elif mode=='image':
  path=config.get('screensaver_image','/media/images/screensaver.rgb')
  try: display.write_rgb565_file(path)
  except Exception: mode='clock'
 if mode=='clock':
  last=-1
  while touch.read() is None:
   now=time.ticks_ms()//1000
   if now!=last:
    last=now; display.fill(PAPER)
    offset=config.get('timezone_minutes',330); hour24=config.get('time_format',24)==24
    display.centred_text(time_service.format_time(offset,hour24),120,INK,PAPER)
    display.centred_text(time_service.format_date(offset),158,MUTED,PAPER)
   time.sleep_ms(100)
 if mode=='blank':
  touch.wait_for_touch(); display.backlight_on(); touch.wait_for_release()
