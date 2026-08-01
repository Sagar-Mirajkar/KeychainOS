"""Reaction-time game."""
import time, random
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer

def run(context):
    d=context.display; d.fill(PAPER); draw_header(d,"Reaction",True)
    d.centred_text("Wait for GO",130,INK,PAPER); draw_footer(d,"Tap early = restart")
    delay=random.randint(1500,4500); start=time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(),start)<delay:
        if context.touch.poll_gesture()=="TAP": return run(context)
        time.sleep_ms(20)
    d.fill(PAPER); draw_header(d,"GO!",False); shown=time.ticks_ms()
    while True:
        if context.touch.poll_gesture()=="TAP":
            result=time.ticks_diff(time.ticks_ms(),shown); d.fill(PAPER); draw_header(d,"Reaction",True)
            d.centred_text(str(result)+" ms",130,INK,PAPER); draw_footer(d,"Tap: Again | Right: Back")
            g=context.touch.capture_gesture(); return "BACK" if g["type"]=="RIGHT" else run(context)
        time.sleep_ms(5)
