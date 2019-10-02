import os
import platform


install_apps = [
    'apps.headbeat',
    'apps.daka',
    'apps.operations',
    'apps.timed_tasks'
]
cache_file = os.path.join(os.path.dirname(__file__), 'wechat.pkl')
console_qr = 2 if platform.linux_distribution() else False
group_name = '打卡群'
notice_group_name = '本科生第一党支部微信群'
max_daka_per_day = 2
from_time = '2019-09-29 07:00:00'