"""Long-press context menu renderer."""
from system.ui import PAPER, INK, CARD, BORDER, TEAL_DARK, SOFT_RED
def choose(display,touch,title,actions):
 actions=list(actions); selected=0
 while True:
  display.fill(PAPER); display.centred_text(title[:28],20,INK,PAPER)
  visible=actions[:6]
  for i,label in enumerate(visible):
   y=58+i*40; bg=CARD
   display.fill_rect(18,y,204,35,bg); display.outline_rect(18,y,204,35,TEAL_DARK if i==selected else BORDER,2 if i==selected else 1)
   display.draw_text(str(label)[:22],28,y+9,SOFT_RED if label in ('Delete','Uninstall') else INK,bg,176)
  g=touch.capture_gesture()
  if not g: continue
  if g['type']=='UP': selected=(selected+1)%len(visible)
  elif g['type']=='DOWN': selected=(selected-1)%len(visible)
  elif g['type']=='TAP':
   row=(g['y']-58)//40
   if 0<=row<len(visible): return visible[row]
  elif g['type']=='RIGHT': return None
