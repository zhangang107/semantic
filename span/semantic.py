# -*- coding:UTF-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-11-14T11:02:12+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: semantic.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T16:34:23+08:00
# @Copyright: Copyright by USTC

import re
import armcal
import copy

def get_pre_state(asms):
    reg = {}
    flag = {'C':0, 'Z':0, 'V':0, 'N':0}
    mem = set()
    for asm in asms:
        for word in asm.split():
            if armcal.check_reg(word) and word not in reg:
                reg[word] = 0
                continue
            if armcal.check_mem(word) and word not in mem:
                mem.add(word)
    return (reg, flag, mem)

def get_post_state(asms, post_state):
    count = 1
    for asm in asms:
        print '     [*]before normal_imm:', asm
        # asm = armcal.normal_imm(asm)
        print '     [*]after normal_imm:', asm
        opt = asm.split()[0].lower().rstrip('s')
        if opt in armcal.execute_dic:
            print '[+:%d]%s in dict' %(count, opt)
            armcal.execute_dic[opt](asm, post_state)
        else:
            print '[-:%d]%s not in dict' %(count, opt)
            pass
        count += 1

def get_state(asms):
    _asms = map(lambda s:' '.join(s.split()), asms)
    pre_state = list(get_pre_state(_asms))
    # print 'pre_state:'
    # print pre_state
    post_state = copy.deepcopy(pre_state)
    get_post_state(_asms, post_state)
    # print 'post_state'
    # print post_state
    return pre_state,post_state

def get_diff_semantic(semantic_o, semantic_p, threshold):
    # print semantic_o
    semantic_o = map(armcal.delete_comment, semantic_o)
    # print semantic_o
    semantic_p = map(armcal.delete_comment, semantic_p)
    pre_state_o, post_state_o = get_state(semantic_o)
    # pre_state_p, post_state_p = get_state(semantic_p)
    # difference = 0
    # count = 0
    # print "post_state_p:{}".format(post_state_p)
    # print '\n'
    # print "post_state_o:{}".format(post_state_o)
    # for reg in post_state_p[0]:
    #     count += 1
    #     if reg not in post_state_o[0] or post_state_p[0][reg] != post_state_o[0][reg]:
    #         difference += 1
    # for flag in post_state_p[1]:
    #     count += 1
    #     if flag not in post_state_o[1] or post_state_p[1][flag] != post_state_o[1][flag]:
    #         difference += 1
    # for mem in post_state_p[2]:
    #     count += 1
    #     if mem not in post_state_o[2]:
    #         difference += 1
    # diffrota = difference / float(count)
    # print '[+]difference: {}'.format(difference)
    # print '[+]count: {}'.format(count)
    # print "[+]diffrota: {}".format(diffrota)
    # if diffrota > 0 and diffrota < threshold:
    #     return True
    # else:
    #     return False
    return False

if __name__ == '__main__':
    _asms = map(lambda s:' '.join(s.split()), asms)
    pre_state = get_pre_state(_asms)
    post_state = pre_state.copy()
    get_post_state(_asms, post_state)
