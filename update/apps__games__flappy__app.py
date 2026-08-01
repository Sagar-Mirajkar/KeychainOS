"""Minimal Flappy-style touch game."""
import time, random
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer

def run(context):
    bird_y=150; velocity=0; pipe_x=240; gap_y=130; score=0; last=time.ticks_ms()
    while True:
        now=time.ticks_ms()
        if time.ticks_diff(now,last)>=50:
            last=now; velocity+=1; bird_y+=velocity; pipe_x-=4
            if pipe_x < -28: pipe_x=240; gap_y=random.randint(75,210); score+=1
            if bird_y<38 or bird_y>302 or (58<pipe_x<98 and not gap_y-42<bird_y<gap_y+42):
                return "BACK"
            d=context.display; d.fill(PAPER); draw_header(d,"Flappy",True)
            d.fill_rect(62,bird_y,16,12,INK); d.fill_rect(pipe_x,38,28,max(0,gap_y-80),MUTED)
            d.fill_rect(pipe_x,gap_y+42,28,max(0,278-gap_y),MUTED); draw_footer(d,"Tap: flap | Swipe right: Back")
        g=context.touch.poll_gesture()
        if g=="TAP": velocity=-7
        elif g=="RIGHT": return "BACK"
        time.sleep_ms(5)
