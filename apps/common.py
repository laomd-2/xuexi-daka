import os
import pandas as pd
import datetime
import settings
from .models import Sharing
from sqlalchemy import func, desc
from core import bot, logger, engine, Session


def to_excel(table, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    table.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook  = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('C:C', 50)
    worksheet.set_column('E:E', 20)
    format_invalid_data = workbook.add_format({'font_color': 'red'})
    for index, row in table.iterrows():
        if not row['标题'] or not row['感想']:
            worksheet.set_row(index + 1, cell_format=format_invalid_data)
    writer.save()


def send_report():
    from_time = settings.from_time
    session = Session()
    res = '累计打卡(%s起)\n' % from_time
    for row in session.query(Sharing.name, func.count().label('credit'))\
                               .filter(Sharing.title.isnot(None) & Sharing.thinking.isnot(None))\
                               .group_by(Sharing.name)\
                               .order_by(desc('credit')):
        res += '    %s: %.1f\n' % (row.name, row.credit * 0.2)
    with engine.connect() as con:
        today_daka = pd.read_sql_query(
            "select id,name,title,thinking,strftime('%Y-%m-%d %H:%M:%S', time) as time from sharing where date(time) >= date('now')", con)
        today_daka.rename(inplace=True, columns={
            'id': '序号',
            'name': '姓名',
            'title': '标题',
            'thinking': '感想',
            'time': '时间'
        })
        now = datetime.datetime.now()
        if not os.path.isdir('daka'):
            os.mkdir('daka')
        filename = "daka/%s(00.00.00-%s).xlsx" % (now.date().strftime('%Y-%m-%d'), now.time().strftime('%H.%M.%S'))
        to_excel(today_daka, filename)
        
    for group in bot.groups().search(settings.notice_group_name):
        group.send(res)
        group.send_file(filename)
