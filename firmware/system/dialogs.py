"""Modal touch dialogs."""
def confirm(display,touch,ui,title,message,yes='YES',no='NO',danger=False):
 buttons=(no,yes); geo=ui.draw_dialog(display,title,message,buttons,danger)
 while True:
  g=touch.capture_gesture()
  if g and g.get('type')=='TAP':
   choice=ui.dialog_choice(g['x'],g['y'],buttons,geo)
   if choice: return choice==yes
def alert(display,touch,ui,title,message,danger=False):
 geo=ui.draw_dialog(display,title,message,("OK",),danger)
 while True:
  g=touch.capture_gesture()
  if g and g.get('type')=='TAP' and ui.dialog_choice(g['x'],g['y'],("OK",),geo): return
