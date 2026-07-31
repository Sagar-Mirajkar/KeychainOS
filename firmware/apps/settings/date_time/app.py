"""Date and time settings."""
from system import config,time_service
from system.ui import PAPER,INK,MUTED,draw_header,draw_footer,is_back_tap
def run(context):
 while True:
  c=config.load(); context.display.fill(PAPER); draw_header(context.display,'Date & Time',True)
  context.display.centred_text(time_service.format_time(c.get('timezone_minutes',330),c.get('time_format',24)==24),105,INK,PAPER)
  context.display.centred_text('Tap time: 12/24',150,MUTED,PAPER); context.display.centred_text('Tap lower: NTP sync',180,MUTED,PAPER); draw_footer(context.display,'Back to Settings')
  g=context.touch.capture_gesture()
  if g['type']=='RIGHT' or (g['type']=='TAP' and is_back_tap(g['x'],g['y'])): return 'BACK'
  if g['type']=='TAP' and g['y']<170: config.set('time_format',12 if c.get('time_format',24)==24 else 24)
  elif g['type']=='TAP': time_service.sync()
