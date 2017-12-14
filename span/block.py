# @Author: zhangang <zhangang>
# @Date:   2017-12-12T16:45:52+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: block.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-14T14:26:19+08:00
# @Copyright: Copyright by USTC

import sqlite3
import conf
import networkx as nx
import matplotlib.pyplot as plt
from mydecorator import timefn


output_filename = conf.db_name

# @timefn
def cumulate_item(item_list):
    item_dic = {}
    for item in item_list:
        if item not in item_dic:
            item_dic[item] = 1
        else:
            item_dic[item] += 1
    return item_dic

# @timefn
def cal_degree(node, edges):
    in_degree = 0
    out_degree = 0
    for edge in edges:
        if node == edge[0]:
            out_degree += 1
        if node == edge[1]:
            in_degree += 1
    return (in_degree, out_degree)

# @timefn
def handle_call(mnem_list, opnds_list):
    call_dic = {}
    for i in xrange(len(mnem_list)):
        if mnem_list[i] == 'BL':
            if 'BL' not in call_dic:
                call_dic['BL'] = [opnds_list[i]]
            else:
                call_dic['BL'].append(opnds_list[i])
    return call_dic

@timefn
def readnodesfromsql(func_address, node_table, asm_table):
    conn = sqlite3.connect(output_filename)
    cur = conn.cursor()
    funcname = cur.execute('SELECT FuncName from %s WHERE StartAddress =%d' \
                    % (node_table, func_address)).fetchone()
    funcname = str(funcname[0])
    rows = cur.execute('SELECT BlockId, ChildId, StartAddress, EndAddress FROM \
                                %s WHERE FuncName = "%s"' % (node_table,funcname))
    edges = []
    nodes = {}
    for row in rows:
        src = int(row[0])
        for dst in row[1].split('-'):
            if dst != '':
                edges.append([src, int(dst)])
        nodes[src] = {'funcname':funcname,'startEA':row[2],'endEA':row[3]}
    # degree
    for node_id in nodes:
        in_degree, out_degree = cal_degree(node_id, edges)
        nodes[node_id]['degree'] = {'in_degree':in_degree, 'out_degree':out_degree}
    # get asm info
    for node_id in nodes:
        rows = cur.execute('SELECT Asm, Size, Mnem, OpLen, Opnds, OpTypes, OperandValues\
                    FROM %s WHERE Address>=%d AND Address<%d'%(asm_table, \
                            nodes[node_id]['startEA'], nodes[node_id]['endEA']))
        rows = list(rows)
        asms = map(lambda item:item[0].encode('utf-8'), rows)
        sizes = [item[1] for item in rows]
        # mnem_list = [item[2] for item in rows]
        mnem_list = [item[0].split(' ')[0] for item in rows]
        opnds_list = [item[4] for item in rows]
        optype_list = [item[5] for item in rows]
        nodes[node_id]['asms'] = asms
        nodes[node_id]['sizes'] = sizes
        nodes[node_id]['power'] = len(asms)
        nodes[node_id]['mnem'] = cumulate_item(mnem_list)
        nodes[node_id]['optype'] = cumulate_item([optype for optlist in optype_list for \
                                            optype in optlist.split('~')])
        nodes[node_id]['call'] = call_dic = handle_call(mnem_list, opnds_list)
    cur.close()
    conn.close()
    print 'read %d nodes from sql' % len(nodes)
    return nodes, edges

@timefn
def CreateGraph(nodes,edges):
    # print 'start CreateGraph: %s' %(time.time())
    # Create graph from edges and saveto png
    G = nx.DiGraph()
    # add nodes
    # for node_id in nodes:
    #     G.add_node(node_id,funcname=nodes[node_id]['funcname'],asms=nodes[node_id]['asms'],\
    #                 sizes=nodes[node_id]['sizes'],power=nodes[node_id]['power'])
    G.add_nodes_from(nodes)
    for node_id in nodes:
        G.nodes[node_id].update(nodes[node_id])
    G.add_edges_from(edges)
    # print edges
    # save to png
    nx.draw(G, pos=nx.spring_layout(G), arrows=True, with_labels = True, node_size = 350, node_color='r')
    plt.title('Orign graph')
    plt.savefig('01.png')
    plt.close()
    # end plt
    # print 'end CreateGraph: %s' %(time.time())
    return G

if __name__ == '__main__':
    nodes_f = readnodesfromsql(498972, 'nodesf', 'funcasmf')
    nodes_g = readnodesfromsql(499256, 'nodesg', 'funcasmg')
