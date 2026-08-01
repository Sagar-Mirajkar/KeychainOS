"""Open full-screen .rgb images from /media/images."""
import os
from system import rgb565_viewer
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer, is_back_tap

def run(context):
    folder="/media/images"
    try: names=sorted([n for n in os.listdir(folder) if n.lower().endswith(".rgb")])
    except OSError: names=[]
    index=0
    while True:
        if not names:
            d=context.display; d.fill(PAPER); draw_header(d,"RGB Images",True)
            d.centred_text("No .rgb images found",125,INK,PAPER)
            d.centred_text("Copy 240x320 RGB565 files",155,MUTED,PAPER); draw_footer(d,"Right swipe: Back")
        else:
            rgb565_viewer.show(context.display, folder+"/"+names[index])
        g=context.touch.capture_gesture()
        if g["type"]=="RIGHT" and not names: return "BACK"
        if g["type"]=="RIGHT" and names: index=(index-1)%len(names)
        elif g["type"]=="LEFT" and names: index=(index+1)%len(names)
        elif g["type"]=="TAP" and is_back_tap(g["x"],g["y"]): return "BACK"
        elif g["type"]=="DOWN": return "BACK"
