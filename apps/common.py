import pandas as pd
import sqlite3
import datetime
import settings
from core import bot, logger


def to_excel(table, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    table.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('C:C', 50)
    worksheet.set_column('E:E', 20)
    writer.save()


def send_report():
    from_time = settings.from_time
    with sqlite3.connect('party.db3') as con:
        con.set_trace_callback(logger.info)
        cur = con.cursor()
        cur.execute("select name, count(*) * 0.2 as credit from sharing \
            where title is not null and thinking is not null\
                 and datetime(time)>='%s'\
            group by name order by credit desc" % from_time)
        today_daka = pd.read_sql_query(
            "select * from sharing where date(time) >= date('now')", con)
        today_daka.rename(inplace=True, columns={
            'id': '序号',
            'name': '姓名',
            'title': '标题',
            'thinking': '感想',
            'time': '时间'
        })
        now = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        today, time = now.split(' ')
        filename = "daka/{today}(00.00.00-{time}).xlsx".format(**locals())
        to_excel(today_daka, filename)
        res = '累计打卡(%s起)\n' % from_time
        for row in cur.fetchall():
            res += '    %s: %.1f\n' % (row[0], round(row[1], 1))
        for group in bot.groups().search(settings.notice_group_name):
            group.send(res)
            group.send_file(filename)
