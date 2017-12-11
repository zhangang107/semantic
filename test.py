# @Author: zhangang <zhangang>
# @Date:   2017-12-11T10:58:38+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: test.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T11:10:24+08:00
# @Copyright: Copyright by USTC

from span.asm_txt2sqlv0 import asm_put2sql
from span.csv2sqlv1 import nodes_put2sql

asm_put2sql('./data/asm_f.txt', 'FuncAsmF')
asm_put2sql('./data/asm_g.txt', 'FuncAsmG')

nodes_put2sql('./data/node_f.csv', 'NodesF')
nodes_put2sql('./data/node_g.csv', 'NodesG')

print 'read 2 sql complied...'
