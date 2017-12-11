#!/usr/bin/python
#*-*utf-8*-*
# @Author: zhangang <zhangang>
# @Date:   2017-11-01T15:44:28+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: asm_txt2sqlv0.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T14:19:43+08:00
# @Copyright: Copyright by USTC

import sqlite3
from mydecorator import timefn
import conf

# input_filename = 'func_asm.txt'
output_filename = conf.db_name
@timefn
def creattb(output_filename, table_name):
    try:
        conn = sqlite3.connect(output_filename)
        cur = conn.cursor()
        cur.execute('CREATE TABLE %s (Id INTEGER PRIMARY KEY, Address INTEGER,\
                        Size INTEGER, Asm char(100))' % table_name)
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
    cur.executemany('INSERT INTO %s (Address, Size, Asm) VALUES (?, ?, ?)' % table_name,data)

    conn.commit()
    cur.close()

@timefn
def asm_put2sql(input_filename, table_name, output_filename = output_filename):
    f = open(input_filename)
    #f.readline()
    creattb(output_filename, table_name)
    data = []
    # conn = sqlite3.connect(output_filename)
    for strline in f.readlines():
        strlist = strline.strip('\n').split('&')
        data.append(strlist)
        # insert_db_table(conn, strlist[0], strlist[1], strlist[2])
    # conn.close()
    insert_many_to_table(output_filename, table_name, data)
    f.close()
    # print 'write to sql done.'
