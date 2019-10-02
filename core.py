import settings
import wxpy
import time
import logging

bot: wxpy.Bot = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('xuexi')

def start():
    global bot
    while True:
        bot = wxpy.Bot(console_qr = getattr(settings, 'console_qr', False),
                       cache_path=getattr(settings, 'cache_file', None))
        for module in settings.install_apps:
            __import__(module)
        bot.join()
        time.sleep(2)