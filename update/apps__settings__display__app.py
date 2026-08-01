"""Basic display settings placeholder with current values."""
from system.ui import PAPER, INK, MUTED, draw_header, draw_footer

def run(context):
    d=context.display; d.fill(PAPER); draw_header(d,"Display",True)
    d.centred_text("Theme: E-paper Minimal",105,INK,PAPER)
    d.centred_text("Brightness: 100%",140,MUTED,PAPER)
    d.centred_text("Refresh: Low flicker",175,MUTED,PAPER)
    draw_footer(d,"Tap or swipe right: Back"); context.touch.capture_gesture(); return "BACK"
