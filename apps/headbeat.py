import wxpy
from datetime import datetime
from core import bot
from apscheduler.schedulers.background import BackgroundScheduler

#scheduler = BackgroundScheduler()
#scheduler.add_job(lambda: bot.file_helper.send_msg('%s: this is a heart beat message!!!' % datetime.now()), 
 #                 'interval', seconds=60)
#scheduler.start()

@bot.register(bot.file_helper, wxpy.TEXT, except_self=False)
def alive_reply(msg):
    return 'alive'
