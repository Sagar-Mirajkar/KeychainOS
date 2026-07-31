"""Friendly exception screen and terminal traceback."""
import sys
def show(display,touch,ui,title,error):
 try: sys.print_exception(error)
 except Exception: print(title,repr(error))
 ui.draw_error(display,title,error)
 while True:
  g=touch.capture_gesture()
  if g and (g['type']=='RIGHT' or (g['type']=='TAP' and ui.is_back_tap(g['x'],g['y']))): return
