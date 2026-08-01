"""Simple five-minute countdown timer."""
import time
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer, is_back_tap

def run(context):
    remaining=300000; running=False; started=time.ticks_ms(); last=-1
    while True:
        now=time.ticks_ms(); value=max(0, remaining-(time.ticks_diff(now,started) if running else 0))
        second=value//1000
        if second != last:
            last=second; d=context.display; d.fill(PAPER); draw_header(d,"Timer",True)
            d.centred_text("%02d:%02d"%(second//60,second%60),125,INK,PAPER)
            d.centred_text("Tap: Start/Pause",165,MUTED,PAPER); draw_footer(d,"Swipe down: Reset | Right: Back")
        if value==0 and running: running=False; remaining=0
        g=context.touch.wait_gesture(timeout_ms=100)
        if not g: continue
        if g["type"]=="RIGHT" or (g["type"]=="TAP" and is_back_tap(g["x"],g["y"])): return "BACK"
        if g["type"]=="DOWN": remaining=300000; running=False; last=-1
        elif g["type"]=="TAP":
            if running: remaining=value; running=False
            else: started=now; running=True
