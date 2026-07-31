"""Local two-player Tic-Tac-Toe."""
from system.ui import PAPER,INK,TEAL_DARK,SOFT_RED,draw_header,draw_footer,is_back_tap
X0=21; Y0=66; CELL=66
def winner(b):
 lines=((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
 for line in lines:
  if b[line[0]] and b[line[0]]==b[line[1]]==b[line[2]]: return b[line[0]]
 return 'DRAW' if all(b) else None
def draw(context,b,turn):
 d=context.display; d.fill(PAPER); draw_header(d,'Tic Tac Toe',True)
 for i in (1,2): d.fill_rect(X0+i*CELL-1,Y0,3,CELL*3,INK); d.fill_rect(X0,Y0+i*CELL-1,CELL*3,3,INK)
 d.outline_rect(X0,Y0,CELL*3,CELL*3,INK,2)
 for i,v in enumerate(b):
  if v: d.centred_text('',0); d.draw_text(v,X0+(i%3)*CELL+29,Y0+(i//3)*CELL+25,SOFT_RED if v=='X' else TEAL_DARK,PAPER,8)
 draw_footer(d,'Player %s | Tap square'%turn)
def run(context):
 while True:
  b=['']*9; turn='X'
  while True:
   draw(context,b,turn); g=context.touch.capture_gesture()
   if g['type']=='RIGHT' or (g['type']=='TAP' and is_back_tap(g['x'],g['y'])): return 'BACK'
   if g['type']!='TAP' or not(X0<=g['x']<X0+CELL*3 and Y0<=g['y']<Y0+CELL*3): continue
   index=((g['y']-Y0)//CELL)*3+(g['x']-X0)//CELL
   if b[index]: continue
   b[index]=turn; result=winner(b)
   if result:
    draw(context,b,turn); context.display.centred_text('DRAW' if result=='DRAW' else result+' WINS',45,INK,PAPER)
    g=context.touch.capture_gesture()
    if g['type']=='RIGHT' or (g['type']=='TAP' and is_back_tap(g['x'],g['y'])): return 'BACK'
    break
   turn='O' if turn=='X' else 'X'
