"""Wi-Fi Settings app."""
from system import wifi_manager, keyboard
def run(context):
 return 'CONNECTED' if wifi_manager.setup_touch(context.display,context.touch,context.ui,keyboard) else 'BACK'
