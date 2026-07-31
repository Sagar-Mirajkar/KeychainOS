"""KeychainOS Clock app."""
import time
from system import time_service
from system.ui import PAPER,INK,MUTED,draw_header,draw_footer,is_back_tap
def run(context):
 hour24=context.config.get('time_format',24)==24; offset=context.config.get('timezone_minutes',330); last=-1
 while True:
  now=time.ticks_ms()//1000
  if now!=last:
   last=now; context.display.fill(PAPER); draw_header(context.display,'Clock',True)
   context.display.centred_text(time_service.format_time(offset,hour24),120,INK,PAPER)
   context.display.centred_text(time_service.format_date(offset),156,MUTED,PAPER); draw_footer(context.display,'Tap time: 12/24 | Back')
  g=context.touch.poll_gesture()
  if not g: time.sleep_ms(30); continue
  if g['type']=='RIGHT' or (g['type']=='TAP' and is_back_tap(g['x'],g['y'])): return 'BACK'
  if g['type']=='TAP' and 90<=g['y']<190: hour24=not hour24
