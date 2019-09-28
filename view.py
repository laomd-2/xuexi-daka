import time
import sqlite3
from pprint import pprint

with sqlite3.connect('party.db3') as con:
    cur = con.cursor()
    while True:
        pprint(cur.execute("PRAGMA table_info('sharing')").fetchall())
        cur.execute("select * from sharing")
        for row in cur.fetchall():
            print(row)
        print('-' * 30)
        time.sleep(2)
