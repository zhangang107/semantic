#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-12-13T16:36:42+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: similarity.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-13T17:13:00+08:00
# @Copyright: Copyright by USTC

from math import sqrt


'''
余弦相似度
'''
def sim_distance_cos(p1, p2):
    c = set(p1.keys())&set(p2.keys())
    if not c:
        return 0
    ss = sum([p1.get(sk)*p2.get(sk) for sk in c])
    sq1 = sqrt(sum([pow(sk, 2) for sk in p1.values()]))
    sq2 = sqrt(sum([pow(sk, 2) for sk in p2.values()]))
    p = float(ss)/(sq1*sq2)
    return p

'''
span.block 查找补丁中与原节点相似度最高的节点
eg:
    block id: 6
    power: 3
    {u'LDR': 1, u'B': 1, u'CMP': 1}  助记符
    {u'1': 2, u'5': 1, u'4': 1, u'7': 1} 操作数类型
    {}
先比较助记符
输入 nodes_f nodes_g
返回相似度高的两个节点 [(node_f, node_g)]
'''
def find_sim_node_pair(nodes_f, nodes_g, similarity):
    # 先只比较助记符
    # 选取相似度高的前几位
    # 判断是否大于阈值， 大于则为候选
    # 考虑函数调用序列 call str不便用相似度算法比较 只有等于或不等于
    # 考虑语句大小
    # 考虑节点相互关系
    # 考虑出入度
    threshold_sim = 0.90
    threshold_sam = 0.99
    prefs = {}
    node_pair = []
    nodes_power_g = {}
    nodes_optype_g = {}
    nodes_greed_g = {}
    for node in nodes_g:
        prefs[node] = nodes_g[node]['mnem']
        # print 'origin :\n', prefs[node]
        nodes_power_g[node] = {'power':nodes_g[node]['power']}
        # print 'power:',nodes_power_g[node]
        nodes_optype_g[node] = nodes_g[node]['optype']
        nodes_greed_g[node] = nodes_g[node]['degree']
        prefs[node].update(nodes_power_g[node])
        # print 'after update power:\n', prefs[node]
        prefs[node].update(nodes_optype_g[node])
        prefs[node].update(nodes_greed_g[node])
    for node in nodes_f:
        match_pair = []
        p1 = nodes_f[node]['mnem']
        node_power_f = {'power':nodes_f[node]['power']}
        p1.update(node_power_f)
        node_optype_f = nodes_f[node]['optype']
        p1.update(node_optype_f)
        node_greed_f = nodes_f[node]['degree']
        p1.update(node_greed_f)
        match_list = topMatches(prefs, p1, 3, similarity)
        for match in match_list:
            sim, node_g = match
            if sim >= threshold_sim and check_call(nodes_f[node]['call'], nodes_g[node_g]['call']):
                match_pair.append((node, node_g, sim))
            else:
                print node, node_g, sim
        node_pair.append(match_pair)
    return node_pair

'''
比较函数调用序列
'''
def check_call(node_f_call, node_g_call):
    return node_f_call == node_g_call

'''
得到top相似度高的前几位
'''
def topMatches(prefs, person, n, similarity):
    scores = [(similarity(person, prefs.get(other)), other) for other in prefs]
    result = sorted(scores, key=lambda scores: (-scores[0], scores[1]))
    return result[0:n]
