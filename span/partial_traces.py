# -*- coding:UTF-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-11-07T10:51:25+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: partial_traces.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-14T14:28:14+08:00
# @Copyright: Copyright by USTC
import networkx
from collections import deque
from similarity import sim_distance_cos, find_sim_node_pair
from mydecorator import timefn

'''
待修改
现在是先获得了对应基本块
反求出不同块（无对应块）
再根据一阶领域， 在原始函数中圈出 partial_traces
所以要修改的函数为涉及基本块比对的函数
`get_partial_traces`
`CheckSameBlock`
`convert_node`
'''
# def get_partial_traces(graph_o, graph_p):
#     # 对每个基本块标记
#     # 过滤已标记块
#     partial_traces = []
#     Bnodes = []
#     tags = {}
#     nodes_p = list(graph_p.nodes())
#     nodes_o = list(graph_o.nodes())
#     for i, node_p in enumerate(nodes_p):
#         for node_o in nodes_o:
#             if CheckSameBlock(graph_o, node_o, graph_p, node_p):
#                 nodes_o.remove(node_o)
#                 tags[i] = node_o
#                 break
#         Bnodes.append(node_p)
#     traces_p = LinerConnectedComponents(graph_p, Bnodes)
#     for trace_p in traces_p:
#         neighbors = GetFirstDegreeNeigbors(graph_p, trace_p)
#         neighbors = convert_node(neighbors, tags)
#         Blocks_o = GetRelevantOriginalBlocks(graph_o, neighbors,)
#         traces_o = LinerConnectedComponents(graph_o, Blocks_o)
#         partial_traces.append((trace_p, traces_o))
#     return partial_traces

tags = {}
threshold_sam = 0.99

def partial_traces2nodes(partial_traces):
    nodes_o_list = []
    nodes_p_list = []
    for partial_trace in partial_traces:
        nodes_o_list.append([node for trace in partial_trace[1] for node in trace])
        nodes_p_list.append(partial_trace[0])
    return nodes_o_list, nodes_p_list


# @timefn
def get_same_tag(nodes_o, nodes_p):
    nodes_pair = find_sim_node_pair(nodes_o, nodes_p, sim_distance_cos)
    print nodes_pair
    node_o_visted = set()
    for pairs in nodes_pair:
        if pairs:
            node_o, node_p, sim = pairs[0]
            if node_o not in node_o_visted:
                node_o_visted.add(node_o)
                if sim >= threshold_sam:
                    tags[node_p] = node_o
            else:
                print 'error: same node_o in node_pair'

@timefn
def get_partial_traces(graph_o, graph_p):
    partial_traces = []
    Bnodes = []
    nodes_p = dict(graph_p.nodes())
    nodes_o = dict(graph_o.nodes())
    get_same_tag(nodes_o, nodes_p)
    diff_nodes_p = [ node for node in nodes_p if node not in tags]
    diff_nodes_o = [node for node in nodes_o if node not in tags.values()]
    print "tags:",tags
    print 'bnodes:',diff_nodes_p
    traces_p = LinerConnectedComponents(graph_p, diff_nodes_p)
    print "trace_p:", traces_p
    for trace_p in traces_p:
        neighbors = GetFirstDegreeNeigbors(graph_p, trace_p)
        print '[+]',neighbors
        neighbors = convert_node(neighbors, tags)
        print '[-]',neighbors
        Blocks_o = GetRelevantOriginalBlocks(graph_o, neighbors, diff_nodes_o)
        print '[1]',Blocks_o
        traces_o = LinerConnectedComponents(graph_o, Blocks_o)
        partial_traces.append((trace_p, traces_o))
    return partial_traces

# @timefn
def convert_node(nodes, tags):
    neighbors = [ tags[node] for node in nodes]
    # upbound = []
    # unbound = []
    # for node in nodes[0]:
    #     upbound.append(tags[node])
    # for node in nodes[1]:
    #     unbound.append(tags[node])
    # neighbors.append(upbound)
    # neighbors.append(unbound)
    return neighbors

# @timefn
def LinerConnectedComponents(graph, Bnodes):
    # 根据节点生成子图，在子图中处理连点成线
    sub_graph = graph.subgraph(Bnodes)
    return CreateLine(sub_graph)

# @timefn
def Travel(graph, start, node_visited,reslist):
    succs = [succ for succ in graph.successors(start) if succ not in node_visited]
    node_visited.append(start)
    reslist.append(start)
    if len(succs) == 0:
        return
    for succ in succs:
        if succ not in node_visited:
            Travel(graph, succ, node_visited, reslist)

# @timefn
def CreateLine(graph):
    nodes = list(graph.nodes())
    lines = []
    while len(nodes) > 0:
        node = nodes[0]
        node_visited = []
        reslist = []
        Travel(graph, node, node_visited, reslist)
        lines.append(reslist)
        for node in reslist:
            nodes.remove(node)
    return lines

# def CheckAsms(asms_o, asms_p):
#     # 在这之前，应进行归一化操作
#     def _getasmcheck(asms):
#         asms = map(normalied, asms)
#         check_dict = {}
#         for asm in asms:
#             for s in asm:
#                 if s in check_dict:
#                     check_dict[s] += 1
#                 else:
#                     check_dict[s] = 1
#         return check_dict
#     return _getasmcheck(asms_o) == _getasmcheck(asms_p)
#
# def CheckSameBlock(graph_o, node_o, graph_p, node_p):
#     # 判断基本块是否相等
#     # 判断属性： pow语句量、出度
#     # 判断asm是否相等
#     asms_o = graph_o.nodes[node_o]['asms']
#     asms_p = graph_p.nodes[node_p]['asms']
#     if len(asms_o) != len(asms_p):
#         return False
#     if len(list(graph_o.successors(node_o))) != \
#         len(list(graph_p.successors(node_p))):
#         return False
#     if not CheckAsms(asms_o,asms_p):
#         return False
#     return True

# @timefn
def GetFirstDegreeNeigbors(graph, line):
    # 获取补丁最近轨迹邻点
    # 上下边界并不是固定的 一个节点既可能是上边界又可能是下边界
    # neighbors = []
    # upbound = []
    # unbound = []
    neighbors = set()
    for node in line:
        for predecess in graph.predecessors(node):
            if predecess not in line:
                # upbound.append(predecess)
                neighbors.add(predecess)
        for succ in graph.successors(node):
            if succ not in line:
                # unbound.append(succ)
                neighbors.add(succ)
    # neighbors.append(upbound)
    # neighbors.append(unbound)
    return neighbors
    # pass

# @timefn
# def GetBlocksByBounds(graph, start_node, neighbors):
#     bounds = neighbors[0] + neighbors[1]
#     degree = 0
#     bounds_visited = []
#     queue = [start_node]
#     blocks = []
#     while len(queue) >0:
#         node = queue.pop(0)
#         blocks.append(node)
#         for predecess in graph.predecessors(node):
#             if predecess not in bounds and predecess not in queue:
#                 queue.append(predecess)
#             if predecess in bounds and predecess not in bounds_visited:
#                 degree += 1
#                 bounds_visited.append(predecess)
#         for succ in graph.successors(node):
#             if succ not in bounds and succ not in queue:
#                 queue.append(succ)
#             if succ in bounds and succ not in bounds_visited:
#                 degree += 1
#                 bounds_visited.append(predecess)
#     return degree, blocks


def check_in_Bound(graph, node, diff_nodes_o, neighbors):
    for succ in graph.successors(node):
        if succ not in neighbors and succ not in diff_nodes_o:
            print 'node {} out from up'.format(node)
            print 'node ', succ
            return False
    for predecess in graph.predecessors(node):
        if predecess not in neighbors and predecess not in diff_nodes_o:
            print 'node {} out from down'.format(node)
            print 'node ', predecess
            return False
    return True

# @timefn
def GetRelevantOriginalBlocks(graph, neighbors, diff_nodes_o):
    # 捕获对应原生块域 原生块域被上下边界所包围
    # 同时与neighbors一阶连通
    # 加入连通度的概念
    # 去掉上下边界
    # 当且仅当与边界一阶连通时，加入partial_traces
    # 连通度的概念 暂时保留
    # bounds = neighbors[0] + neighbors[1]
    # # up = neighbors[0][0]
    # if len(bounds) <= 0:
    #     return list(graph.nodes)
    # up = bounds[0]
    # blocks = []
    # for node in graph.successors(up):
    #     degree, blockstmp = GetBlocksByBounds(graph, node, neighbors)
    #     if degree == len(bounds):
    #         blocks = list(blockstmp)
    #         return blocks
    blocks = []
    for node in diff_nodes_o:
        if check_in_Bound(graph, node, diff_nodes_o, neighbors):
            blocks.append(node)
    return blocks
    # pass
