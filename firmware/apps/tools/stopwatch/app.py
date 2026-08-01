"""Touch stopwatch."""
import time
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer, is_back_tap

def run(context):
    running=False; elapsed=0; started=time.ticks_ms(); last=-1
    while True:
        now=time.ticks_ms()
        value=elapsed + (time.ticks_diff(now, started) if running else 0)
        second=value//1000
        if second != last:
            last=second; d=context.display; d.fill(PAPER); draw_header(d,"Stopwatch",True)
            d.centred_text("%02d:%02d.%d" % (second//60, second%60, (value//100)%10),125,INK,PAPER)
            d.centred_text("Tap: Start/Pause",165,MUTED,PAPER); draw_footer(d,"Swipe down: Reset | Right: Back")
        g=context.touch.wait_gesture(timeout_ms=100)
        if not g: continue
        if g["type"]=="RIGHT" or (g["type"]=="TAP" and is_back_tap(g["x"],g["y"])): return "BACK"
        if g["type"]=="DOWN": running=False; elapsed=0; started=time.ticks_ms(); last=-1
        elif g["type"]=="TAP":
            if running: elapsed += time.ticks_diff(now,started); running=False
            else: started=now; running=True
