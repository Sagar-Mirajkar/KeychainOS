"""Dynamic KeychainOS launcher."""
import gc, time
from system import bootstrap, config, ui
from system.display import get_display
from system.touch import get_touch
from system.app_scanner import get_scanner
from system.app_loader import get_loader, AppLoadError
from system.context import create_context
from system.navigation import Navigation
from system import error_handler, screensaver
class Launcher:
 def __init__(self):
  self.display=get_display(); self.touch=get_touch(); self.scanner=get_scanner(); self.loader=get_loader(); self.nav=Navigation(); self.last_input=time.ticks_ms()
 def launch(self,app):
  context=create_context(self.display,self.touch,ui,config.load(),self.scanner,self.loader,navigation=self.nav,app_manifest=app)
  try: return self.loader.run(app,context)
  except Exception as error: error_handler.show(self.display,self.touch,ui,app.get('name','App'),error)
 def category(self,category):
  selected=0
  while True:
   apps=self.scanner.scan_apps(category,force=True); ui.draw_grid(self.display,apps,selected,category['name'],True)
   g=self.touch.capture_gesture(); self.last_input=time.ticks_ms()
   if g['type']=='LEFT' and apps: selected=(selected+1)%len(apps)
   elif g['type']=='RIGHT': return
   elif g['type']=='DOWN': apps=self.scanner.refresh_category(category['id']); selected=0
   elif g['type']=='TAP':
    if ui.is_back_tap(g['x'],g['y']): return
    idx=ui.item_at(g['x'],g['y'],apps,selected)
    if idx is not None: self.launch(apps[idx])
 def run(self):
  bootstrap.ensure_structure(); self.display.init()
  if not self.touch.init(): raise RuntimeError('Touch controller not found')
  selected=0
  while True:
   categories=self.scanner.scan_categories(force=True); ui.draw_grid(self.display,categories,selected,'KeychainOS',False)
   timeout=int(config.get('screen_timeout_seconds',60))*1000
   g=self.touch.poll_gesture()
   if g is None:
    if timeout>0 and time.ticks_diff(time.ticks_ms(),self.last_input)>timeout:
     screensaver.run(self.display,self.touch,config.load()); self.last_input=time.ticks_ms()
    time.sleep_ms(15); continue
   self.last_input=time.ticks_ms()
   if g['type']=='LEFT' and categories: selected=(selected+1)%len(categories)
   elif g['type']=='RIGHT' and categories: selected=(selected-1)%len(categories)
   elif g['type']=='DOWN': categories=self.scanner.refresh_all(); selected=0
   elif g['type']=='TAP':
    idx=ui.item_at(g['x'],g['y'],categories,selected)
    if idx is not None: self.category(categories[idx])
   gc.collect()
