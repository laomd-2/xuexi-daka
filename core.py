import settings
import wxpy
import time
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

bot: wxpy.Bot = None
engine = create_engine(settings.db_uri)
Session = sessionmaker(bind=engine)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('xuexi')

def start():
    global bot
    while True:
        bot = wxpy.Bot(console_qr = getattr(settings, 'console_qr', False),
                       cache_path=getattr(settings, 'cache_file', None))
        for module in settings.install_apps:
            __import__(module)
        Base.metadata.create_all(engine)
        bot.join()
        time.sleep(2)