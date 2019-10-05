import os
import platform


install_apps = [
    'apps.headbeat',
    'apps.daka',
    'apps.operations',
    'apps.report'
]
cache_file = os.path.join(os.path.dirname(__file__), 'wechat.pkl')
console_qr = False
group_name = '打卡群'
notice_group_name = '打卡结果群'
min_thinking_len = 50
max_daka_per_day = 2
from_time = '2019-09-29 07:00:00'
db_name = 'party.db3'