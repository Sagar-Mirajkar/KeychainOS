"""KeychainOS selective Update settings app."""
import machine
from system import updater
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer


def run(context):
    display=context.display
    display.fill(PAPER); draw_header(display,"Update",True)
    display.centred_text("Tap centre to check",120,INK,PAPER)
    display.centred_text("Only changed files install",150,MUTED,PAPER)
    draw_footer(display,"Right swipe: Back")
    gesture=context.touch.capture_gesture()
    if gesture["type"]=="RIGHT": return "BACK"

    def progress(index,total,path,state):
        display.fill(PAPER); draw_header(display,"Updating",False)
        display.centred_text("%d of %d"%(index,total),95,INK,PAPER)
        display.centred_text(path.rsplit("/",1)[-1][:28],130,MUTED,PAPER)
        display.centred_text(state.upper(),160,MUTED,PAPER)

    try:
        count=updater.update(progress)
        display.fill(PAPER); draw_header(display,"Updated",False)
        display.centred_text("%d file(s) installed"%count,120,INK,PAPER)
        display.centred_text("Tap to restart",155,MUTED,PAPER)
        context.touch.capture_gesture(); machine.reset()
    except Exception as error:
        display.fill(PAPER); draw_header(display,"Update failed",True)
        display.centred_text(type(error).__name__[:28],110,INK,PAPER)
        display.centred_text(str(error)[:28],140,MUTED,PAPER)
        draw_footer(display,"Tap or swipe right: Back")
        context.touch.capture_gesture()
        return "BACK"
