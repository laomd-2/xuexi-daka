import wxpy
import settings
import sqlite3
from core import bot, logger
from wxpy.utils.misc import get_text_without_at_bot
from .common import send_report


@bot.register(bot.groups().search(settings.notice_group_name), wxpy.TEXT, except_self=False)
def operations(msg):
    if msg.is_at:
        text = get_text_without_at_bot(msg).strip()
        if '今日打卡' == text:
            send_report()
        elif '打卡改名为' in text:
            origin, new = text.split('打卡改名为')
            with sqlite3.connect('party.db3') as con:
                con.set_trace_callback(logger.info)
                cur = con.cursor()
                cur.execute(
                    "update sharing set name='%s' where name='%s'" % (new, origin))
