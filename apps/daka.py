import wxpy
import sqlite3
import settings
import threading
from collections import defaultdict
from core import bot, logger
from xml.etree import ElementTree as ETree

locks = defaultdict(threading.Lock)


def get_column(msg_type):
    return 'title' if msg_type == wxpy.SHARING else 'thinking'


def upsert(user, title_or_thinking, text, time):
    with sqlite3.connect('party.db3') as con:
        con.set_trace_callback(logger.info)
        cur = con.cursor()
        time_filter = "datetime(time) >= '{today} 00:00:00' and datetime(time) <= '{today} 23:59:59'".format(
            today=time.split(' ')[0])
        # ensure unique
        cur.execute("select id from sharing where name='%s' and title is not null and thinking is not null\
            and %s limit 2" % (user, time_filter))
        res = cur.fetchall()
        if len(res) >= settings.max_daka_per_day:
            return
        cur.execute("select id from sharing where name='%s' and %s='%s'" %
                    (user, title_or_thinking, text))
        if not cur.fetchone():
            cur.execute("select id from sharing where name='{user}' and \
              {title_or_thinking} is null and {time_filter}".format(**locals()))
            res = cur.fetchone()
            if res:
                sql = "update sharing set %s='%s', time='%s' where id=%d" % (
                    title_or_thinking, text, time, res[0])
                cur.execute(sql)
            else:
                cur.execute("insert into sharing(name, %s, time) values(?,?,?)" %
                            title_or_thinking, (user, text, time))
            con.commit()


@bot.register(bot.groups().search(settings.group_name), [wxpy.SHARING, wxpy.TEXT, wxpy.NOTE], except_self=False)
def on_msg(msg):
    msg_type = msg.type
    from_user = msg.member.name
    now = msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
    # logger.info("receive a message of type %s。" % msg_type)
    # 处理撤回的消息
    if msg_type == wxpy.NOTE:
        revoked = ETree.fromstring(msg.raw['Content'].replace(
            '&lt;', '<').replace('&gt;', '>')).find('revokemsg')
        if revoked:
            # 根据找到的撤回消息 id 找到 bot.messages 中的原消息
            revoked_msg = bot.messages.search(
                id=int(revoked.find('msgid').text))[0]
            if not revoked_msg:
                return
            with sqlite3.connect('party.db3') as con, locks[from_user]:
                con.set_trace_callback(logger.info)
                cur = con.cursor()
                title_or_thinking = get_column(revoked_msg.type)
                cur.execute("update sharing set %s=null where name='%s' and %s='%s'" %
                            (title_or_thinking, from_user,
                             title_or_thinking, revoked_msg.text)
                            )
                con.commit()
    else:
        with locks[from_user]:
            upsert(from_user, get_column(msg_type), msg.text, now)
