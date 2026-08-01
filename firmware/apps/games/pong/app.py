"""Single-player pocket Pong."""
import time
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer

def run(context):
    bx=120; by=150; dx=3; dy=3; paddle=95
    while True:
        bx+=dx; by+=dy
        if bx<4 or bx>232: dx=-dx
        if by<38: dy=-dy
        if by>280:
            if paddle-25 <= bx <= paddle+45: dy=-abs(dy)
            else: return "BACK"
        g=context.touch.poll_gesture()
        if g=="LEFT": paddle=max(0,paddle-12)
        elif g=="RIGHT": paddle=min(170,paddle+12)
        elif g=="DOWN": return "BACK"
        d=context.display; d.fill(PAPER); draw_header(d,"Pong",True)
        d.fill_rect(bx,by,8,8,INK); d.fill_rect(paddle,286,70,8,MUTED); draw_footer(d,"Swipe left/right | Down: Back")
        time.sleep_ms(30)
