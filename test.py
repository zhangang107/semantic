#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-12-11T10:58:38+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: test.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T14:55:00+08:00
# @Copyright: Copyright by USTC

from span.asm_txt2sqlv0 import asm_put2sql
from span.csv2sqlv1 import nodes_put2sql
import sqlite3
from span import conf
from span.semantic import get_diff_semantic

def put2sql():
    asm_put2sql('./data/asm_f.txt', 'FuncAsmF')
    asm_put2sql('./data/asm_g.txt', 'FuncAsmG')
    nodes_put2sql('./data/node_f.csv', 'NodesF')
    nodes_put2sql('./data/node_g.csv', 'NodesG')
    print 'read 2 sql complied...'

def get_from_sql():
    conn = sqlite3.connect(conf.db_name)
    cur = conn.cursor()
    asms_f = cur.execute('SELECT Asm FROM funcasmf').fetchall()
    asms_f = map(lambda x: x[0].encode('utf-8'), asms_f)
    asms_g = cur.execute('SELECT Asm FROM funcasmg').fetchall()
    asms_g = map(lambda x: x[0].encode('utf-8'), asms_g)
    print len(asms_f)
    print len(asms_g)
    return asms_f, asms_g

def diff(asms_f, asms_g, threshold):
    if get_diff_semantic(asms_f, asms_g, threshold):
        print "[*]found security patches"
    else:
        print "[*]found non-security patches"

asms_f, asms_g = get_from_sql()
diff(asms_f, asms_g, 0.1)
