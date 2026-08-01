"""Device information page."""
import gc, os, sys
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer

def run(context):
    d=context.display; d.fill(PAPER); draw_header(d,"Device Info",True)
    lines=("ESP32-S3 N8R8","MicroPython "+str(sys.implementation.version),"Free RAM: "+str(gc.mem_free()),"Files: "+str(len(os.listdir('/'))))
    for i,line in enumerate(lines): d.draw_text(str(line)[:28],16,78+i*34,INK,PAPER,208)
    draw_footer(d,"Tap or swipe right: Back"); context.touch.capture_gesture(); return "BACK"
