"""Screensaver selection."""
from system import config
from system.ui import draw_grid,is_back_tap
MODES=('clock','blank','image')
def run(context):
 selected=MODES.index(config.get('screensaver','clock')) if config.get('screensaver','clock') in MODES else 0
 while True:
  items=[{'name':m.title()} for m in MODES]; draw_grid(context.display,items,selected,'Screensaver',True); g=context.touch.capture_gesture()
  if g['type']=='RIGHT' or (g['type']=='TAP' and is_back_tap(g['x'],g['y'])): return 'BACK'
  if g['type']=='LEFT': selected=(selected+1)%len(items)
  elif g['type']=='TAP':
   idx=context.ui.item_at(g['x'],g['y'],items,selected)
   if idx is not None: config.set('screensaver',MODES[idx]); return 'SAVED'
