import wxpy
import settings
from core import bot, logger, Session
from wxpy.utils.misc import get_text_without_at_bot
from .models import Sharing
from .common import send_report


@bot.register(bot.groups().search(settings.notice_group_name), wxpy.TEXT, except_self=False)
def operations(msg):
    if msg.is_at:
        text = get_text_without_at_bot(msg).strip()
        if '今日打卡' == text:
            send_report()
        elif '打卡改名为' in text:
            if msg.sender != bot.self:
                return "没有权限"
            origin, new = text.split('打卡改名为')
            session = Session()
            sharings = session.query(Sharing).filter(Sharing.name.like('%' + origin + '%')).all()
            for s in sharings:
                s.name = new
            session.commit()
