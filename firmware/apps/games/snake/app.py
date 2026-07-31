"""Nokia-style wraparound Snake."""
import random,time
BLACK=0; GREEN=0x07E0; RED=0xF800; WHITE=0xFFFF; YELLOW=0xFFE0
CELL=12; TOP=48; COLS=20; ROWS=20
def food(snake):
 while True:
  p=(random.randrange(COLS),random.randrange(ROWS))
  if p not in snake:return p
def cell(d,p,c): d.fill_rect(p[0]*CELL+1,TOP+p[1]*CELL+1,CELL-2,CELL-2,c)
def run(context):
 d=context.display; t=context.touch
 while True:
  snake=[(8,10),(7,10),(6,10)]; direction=(1,0); pending=direction; score=0; target=food(snake); d.fill(BLACK)
  d.draw_text('< BACK',8,10,WHITE,BLACK,48); cell(d,target,RED)
  for part in snake: cell(d,part,GREEN)
  last=time.ticks_ms()
  while True:
   g=t.poll_gesture()
   if g:
    k=g['type']
    if k=='UP' and direction!=(0,1):pending=(0,-1)
    elif k=='DOWN' and direction!=(0,-1):pending=(0,1)
    elif k=='LEFT' and direction!=(1,0):pending=(-1,0)
    elif k=='RIGHT' and direction!=(-1,0):pending=(1,0)
    elif k=='TAP' and g['x']<70 and g['y']<45:return 'BACK'
   if time.ticks_diff(time.ticks_ms(),last)<max(70,180-score*4): time.sleep_ms(5); continue
   last=time.ticks_ms(); direction=pending; h=snake[0]; new=((h[0]+direction[0])%COLS,(h[1]+direction[1])%ROWS)
   if new in snake: break
   snake.insert(0,new); cell(d,new,GREEN)
   if new==target: score+=1; target=food(snake); cell(d,target,RED)
   else: cell(d,snake.pop(),BLACK)
  d.centred_text('GAME OVER',130,RED,BLACK); d.centred_text('Tap retry | Back exit',160,YELLOW,BLACK)
  while True:
   g=t.capture_gesture()
   if g['type']=='RIGHT' or (g['type']=='TAP' and g['x']<70 and g['y']<45): return 'BACK'
   if g['type']=='TAP': break
