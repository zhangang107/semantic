# @Author: zhangang <zhangang>
# @Date:   2017-10-11T11:02:48+08:00
# @Email:  zhanganguc@gmail.com
# @Last modified by:   zhangang
# @Last modified time: 2017-12-14T15:55:38+08:00
# @Copyright: Copyright by USTC

#!/usr/bin/python
#*-*utf-8*-*
import csv
import sqlite3
from mydecorator import timefn
import conf

# input_filename = 'test2sqlv2.csv'
output_filename = conf.db_name

@timefn
def creattb(output_filename, table_name):
    try:
        conn = sqlite3.connect(output_filename)
        cur = conn.cursor()
        cur.execute('CREATE TABLE %s (Id INTEGER PRIMARY KEY, FuncName char(100),\
                        BlockId INTEGER, StartAddress INTEGER, EndAddress INTEGER, ChildId char(100))' % table_name)
        conn.commit()
        cur.close()
    except sqlite3.OperationalError:
        print 'sql Error!\n'

# @timefn
# def insert_db_table(c1, c2, c3, c4, c5):
#     conn = sqlite3.connect(output_filename)
#     cur = conn.cursor()
#     cur.execute('INSERT INTO NoteV0 (FuncName, BlockId, StartAddress, EndAddress, ChildId) VALUES (?, ?, ?, ?, ?)',\
#                 (c1, c2, c3, c4, c5))
#     conn.commit()
#     cur.close()

@timefn
def insert_many_to_table(output_filename, table_name, data):
    conn = sqlite3.connect(output_filename)
    cur = conn.cursor()
    cur.executemany('INSERT INTO %s (FuncName, BlockId, StartAddress, \
        EndAddress, ChildId) VALUES (?, ?, ?, ?, ?)' % table_name, data)
    conn.commit()
    cur.close()

@timefn
def nodes_put2sql(input_filename, table_name, output_filename=output_filename):
    f = open(input_filename)
    creattb(output_filename, table_name)
    reader = csv.reader(f)
    data = []
    for c1, c2, c3, c4, c5 in reader:
        # insert_db_table(c1, c2, c3, c4, c5)
        data.append([c1, c2, c3, c4, c5])
    insert_many_to_table(output_filename, table_name, data)
    f.close()
