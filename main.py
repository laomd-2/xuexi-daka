import time

import wxpy
import logging
import datetime
import sqlite3
import os
import config
from xml.etree import ElementTree as ETree
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

with sqlite3.connect('party.db3') as con:
    cur = con.cursor()
    cur.execute("""
    create table IF NOT EXISTS sharing(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        title VARCHAR(50) NULL,
        thinking VARCHAR(50) NULL,
        time DATETIME NOT NULL
    )
    """)

def get_column(msg_type):
    return 'title' if msg_type == wxpy.SHARING else 'thinking'

def upsert(user, title_or_thinking, text, time):
    with sqlite3.connect('party.db3') as con:
        con.set_trace_callback(logger.info)
        cur = con.cursor()
        time_filter = "datetime(time) >= '{today} 00:00:00' and datetime(time) <= '{today} 23:59:59'".format(today=time.split(' ')[0])
        # ensure unique
        cur.execute("select id from sharing where name='%s' and title is not null and thinking is not null\
            and %s limit 2" % (user, time_filter))
        res = cur.fetchall()
        if len(res) >= config.max_daka_per_day:
            return
        cur.execute("select id from sharing where name='%s' and %s='%s'" % (user, title_or_thinking, text))
        if not cur.fetchone():
            cur.execute("select id from sharing where name='{user}' and \
              {title_or_thinking} is null and {time_filter}".format(**locals()))
            res = cur.fetchone()
            if res:
                sql = "update sharing set %s='%s', time='%s' where id=%d" % (title_or_thinking, text, time, res[0])
                cur.execute(sql)
            else:
                cur.execute("insert into sharing(name, %s, time) values(?,?,?)" % title_or_thinking, (user, text, time))
            con.commit()

def producer():
    bot = config.bot = wxpy.Bot(console_qr=2, cache_path=os.path.join(os.path.expanduser('~'), 'wechat.pkl'))
    daka = bot.groups().search(config.group_name)
    bot.file_helper.send('我启动啦！')

    @bot.register(daka, [wxpy.SHARING, wxpy.TEXT, wxpy.NOTE], except_self=False)
    def on_msg(msg):
        msg_type = msg.type
        from_user = msg.member.name
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # logger.info("receive a message of type %s。" % msg_type)
        # 处理撤回的消息
        if msg_type == wxpy.NOTE:
            revoked = ETree.fromstring(msg.raw['Content'].replace('&lt;', '<').replace('&gt;', '>')).find('revokemsg')
            if revoked:
                # 根据找到的撤回消息 id 找到 bot.messages 中的原消息
                revoked_msg = bot.messages.search(id=int(revoked.find('msgid').text))[0]
                if not revoked_msg:
                    return
                logger.warning("%s 撤回了一条消息。（%s）" % (from_user, revoked_msg.text))
                with sqlite3.connect('party.db3') as con:
                    con.set_trace_callback(logger.info)
                    cur = con.cursor()
                    title_or_thinking = get_column(revoked_msg.type)
                    cur.execute("update sharing set %s=null where name='%s' and %s='%s'" % 
                        (title_or_thinking, from_user, title_or_thinking, revoked_msg.text)
                    )
                    con.commit()
        else:
            # logger.info("%s 打卡。（%s）" % (from_user, msg.text))
            upsert(from_user, get_column(msg_type), msg.text, now)

    @bot.register([bot.file_helper], [wxpy.TEXT], except_self=False)
    def ask(msg):
        return '亲，我还在线哦！'
    bot.join()

def timedTask():
    from_time = open("from_time.txt").read()
    with sqlite3.connect('party.db3') as con:
        con.set_trace_callback(logger.info)
        cur = con.cursor()
        cur.execute("select name, count(*) * 0.2 as credit from sharing \
            where title is not null and thinking is not null\
                 and datetime(time)>='%s'\
            group by name order by credit desc" % from_time)
        res = '累计打卡(%s起)\n' % from_time
        for row in cur.fetchall():
            res += '    %s: %.1f\n' % (row[0], round(row[1], 1))
        for group in config.bot.groups().search(config.group_name):
            group.send(res)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()  
    # 添加调度任务
    # 调度方法为 timedTask，触发器选择 interval(间隔性)，间隔时长为 2 秒
    scheduler.add_job(timedTask, 'cron', hour=7, minute=0, second=0)
    scheduler.start()
    while True:
        try:
            producer()
        except:
            pass
        time.sleep(2)