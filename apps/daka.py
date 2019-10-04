import wxpy
import settings
import threading
from collections import defaultdict
from core import bot, logger, Session
from datetime import timedelta
from sqlalchemy import func
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from xml.etree import ElementTree as ETree
from .models import Sharing

locks = defaultdict(threading.Lock)


def get_column(msg_type):
    return 'title' if msg_type == wxpy.SHARING else 'thinking'


def upsert(user, title_or_thinking, text, time):
    # ensure unique
    today = time.date()
    tomorrow = today + timedelta(days=1)
    session = Session()
    count = session.query(func.count(Sharing.id))\
        .filter(
            (Sharing.time >= today) &
            (Sharing.time < tomorrow) &
            (Sharing.name == user) &
            (Sharing.title.isnot(None)) &
            (Sharing.thinking.isnot(None))
        ).scalar()
    if count >= settings.max_daka_per_day:
        return

    sharing = session.query(Sharing).filter(
        (Sharing.name == user) & 
        (getattr(Sharing, title_or_thinking) == None)
    ).first()
    if sharing is None:
        sharing = Sharing(**{
            'name': user
        })
        session.add(sharing)
    sharing.time = time
    setattr(sharing, title_or_thinking, text)
    try:
        session.commit()
    except IntegrityError:
        logger.warning('conflict %s: %s' % (title_or_thinking, text))
    except StaleDataError:
        logger.warning('conflict %s: %s' % (title_or_thinking, text))

@bot.register(bot.groups().search(settings.group_name), [wxpy.SHARING, wxpy.TEXT, wxpy.NOTE], except_self=False)
def on_msg(msg):
    msg_type=msg.type
    from_user=msg.member.name
    now=msg.create_time
    # 处理撤回的消息
    if msg_type == wxpy.NOTE:
        revoked=ETree.fromstring(msg.raw['Content'].replace(
            '&lt;', '<').replace('&gt;', '>')).find('revokemsg')
        if revoked:
            # 根据找到的撤回消息 id 找到 bot.messages 中的原消息
            revoked_msg=bot.messages.search(
                id=int(revoked.find('msgid').text))[0]
            if not revoked_msg:
                return
            with locks[from_user]:
                session = Session()
                title_or_thinking=get_column(revoked_msg.type)
                sharing = session.query(Sharing).filter(name=from_user).filter(
                    getattr(Sharing, title_or_thinking) == revoked_msg.text).first()
                setattr(sharing, title_or_thinking, None)
    else:
        with locks[from_user]:
            c = get_column(msg_type)
            min_length = getattr(settings, 'min_thinking_len', 1)
            if c == 'title' or len(msg.text) >= min_length:
                upsert(from_user, c, msg.text, now)
            else:
                logger.warning(msg.text + ' of length %d less than %d' % (len(msg.text), min_length))
