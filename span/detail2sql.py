# @Author: zhangang <zhangang>
# @Date:   2017-12-12T15:06:13+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: detail2sql.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-12T16:09:49+08:00
# @Copyright: Copyright by USTC

import sqlite3
from mydecorator import timefn
import conf

# input_filename = 'func_asm.txt'
output_filename = conf.db_name
@timefn
def altertb(output_filename, table_name):
    try:
        conn = sqlite3.connect(output_filename)
        cur = conn.cursor()
        cur.execute('ALTER TABLE %s ADD COLUMN Mnem char(100)' % table_name)
        cur.execute('ALTER TABLE %s ADD COLUMN OpLen int' % table_name)
        cur.execute('ALTER TABLE %s ADD COLUMN Opnds char(100)' % table_name)
        cur.execute('ALTER TABLE %s ADD COLUMN OpTypes char(100)' % table_name)
        cur.execute('ALTER TABLE %s ADD COLUMN OperandValues char(100)' % table_name)
        conn.commit()
        cur.close()
    except sqlite3.OperationalError:
        print 'sql Error!\n'

# @timefn
# def insert_db_table(conn, c1, c2, c3):
#     # conn = sqlite3.connect(output_filename)
#     cur = conn.cursor()
#     cur.execute('INSERT INTO FuncAsm (Address, Size, Asm) VALUES (?, ?, ?)',\
#                 (c1, c2, c3))
#     conn.commit()
#     # cur.close()

@timefn
def insert_many_to_table(output_filename, table_name, data):
    conn = sqlite3.connect(output_filename)
    cur = conn.cursor()
    cur.executemany('UPDATE %s SET Mnem = ?, OpLen = ?, Opnds = ?, OpTypes = ?, \
                    OperandValues = ? WHERE id = ?'% table_name, data)

    conn.commit()
    cur.close()

@timefn
def detatil_put2sql(input_filename, table_name, output_filename = output_filename):
    f = open(input_filename)
    #f.readline()
    altertb(output_filename, table_name)
    data = []
    # conn = sqlite3.connect(output_filename)
    cnt = 1
    for strline in f.readlines():
        strlist = strline.strip('\n').split('&')
        strlist.append(cnt)
        data.append(strlist)
        cnt += 1
        # insert_db_table(conn, strlist[0], strlist[1], strlist[2])
    # conn.close()
    insert_many_to_table(output_filename, table_name, data)
    f.close()
    print 'write to sql done.'
