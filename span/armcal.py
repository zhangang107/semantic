# -*- coding:UTF-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-11-14T11:02:12+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: semantic.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-08T16:13:42+08:00
# @Copyright: Copyright by USTC

import re
from binstr import BinStr

def delete_comment(arm):
    p = re.compile(r'(.*);(.*)')
    return p.sub(r'\1', arm)

def check_branch(word):
    matchObj = re.search(r'^(B|BL)', word, re.M|re.I)
    # TODO: 添加跳转指令识别
    return matchObj and True or False

def check_reg(word):
    # 寄存器已R开头 或 SP 或 PC
    matchObj = re.search(r'^(R\d+|SP|PC)', word, re.M|re.I)
    return matchObj and True or False

def check_mem(word):
    # 内存位置形如: []或 loc_
    matchObj = re.search(r'^(\[.+\]|loc_)', word, re.M|re.I)
    return matchObj and True or False

def check_flag(word):
    # 此处仅包含 数据处理指令影响的标志位 n z c v
    # TODO:
    matchObj = re.search(r'', word, re.M|re.I)
    return matchObj and True or False

def check_imm(word):
    matchObj = re.search(r'^\#\w+', word, re.M|re.I)
    return matchObj and True or False

def normal_imm(asm):
    def _normal_oper(oper, per='+'):
        res = oper
        if 'var_' in oper:
            p2 = re.compile(r'.*var_(\w+)')
            res = p2.sub(r'\1', oper)
            if per == '+':
                res = '-' + res
        return res
    def _normal(m):
        result = ''
        # print 'start>>>'
        tmp = m.group(1)
        res = ''
        if '+' in tmp:
            # print '+'
            items = [s for s in tmp.split('+') if s !='']
            if len(items) == 1:
                # print '>> +1'
                res = items[0]
                result = _normal_oper(res)
            else:
                # print '>> +2'
                oper1 = _normal_oper(items[0])
                oper2 = _normal_oper(items[1])
                res = int(oper1, 16) + int(oper2, 16)
                result = hex(res)
        elif '-' in tmp:
            # print '-'
            items = [s for s in tmp.split('-') if s !='']
            print items
            if len(items) == 1:
                # print '>> -1'
                res = items[0]
                result = _normal_oper(res, '-')
            else:
                # print '>> -2'
                oper1 = _normal_oper(items[0])
                oper2 = _normal_oper(items[1])
                res = int(oper1, 16) - int(oper2, 16)
                result = hex(res)
        else:
            # print '*'
            result = _normal_oper(tmp)
        result = ' #' + result
        return result
    p1 = re.compile(r'[\w ]+#([+-]?[\w+_]+)')
    return p1.sub(_normal, asm)


def _norma_imm(asm):
    # 消除 ida 带来的形如'SUB R0, R11, #-var_C' 产生的立即数错误
    # ‘#-var_C’ --> #C
    # 改进版 将所有的’'var_C' -->'-C'
    #               '-var_C' --> 'C'
    # eg:       asm1 = 'sub   R0, R11, #-var_C'
    #           asm2 = 'ADD   R3, SP, #0x7c+var_74'
    p = re.compile(r'#-var_(\w+)')
    return p.sub(r'#\1', imm)

def cycle_shift(num, step):
    from collections import deque
    num = deque(bin(num)[2:]) if type(num)==int else deque(num)
    _length = len(num)
    if _length > 32 or step >32:
        print 'ERROR: num out of range or step out 32'
        return None
    for i in range(32-_length):
        num.appendleft('0')
    # print num
    num.rotate(step)
    # print num
    return ''.join([i for i in num])

def asr(num, shift, size=32):
    tmp = int('1'*shift + '0'*(size-shift), 2)
    return num >> shift | tmp

def _shift_imm(shift_operand, post_state):
    global shifter_carry_out
    print shift_operand
    imm = shift_operand[1:]
    print imm
    imm_bin = BinStr(int(imm, 16))
    immed_8 = int(imm_bin[7:0], 2)
    rotate_imm = int(imm_bin[11:8], 2)
    shifter_operand = int(cycle_shift(immed_8, rotate_imm*2), 2)
    if rotate_imm == 0:
        shifter_carry_out = post_state[1]['C']
    else:
        shifter_carry_out = BinStr(shifter_operand)[31]
    return shifter_operand

def _shift_rm(shift_operand, post_state):
    global shifter_carry_out
    shifter_carry_out = post_state[1]['C']
    return get_value(shift_operand[0], post_state)

def _shift_lsl(shift_operand, post_state):
    global shifter_carry_out
    Rm = get_value(shift_operand[0].strip(','), post_state)
    if check_imm(shift_operand[2]):
        shift_imm = int(shift_operand[2][1:], 16)
        if shift_imm == 0:
            shifter_operand = Rm
            shifter_carry_out = post_state[1]['C']
        else:
            shifter_operand = Rm << shift_imm
            shifter_carry_out = BinStr(Rm)[32 - shift_imm]
        return shifter_operand
    elif check_reg(shift_operand[2]):
        Rs = get_value(shift_operand[2], post_state)
        RsBin = int(BinStr(Rs)[7:0], 2)
        if RsBin == 0:
            shifter_operand = Rm
            shifter_carry_out = post_state[1]['C']
        elif RsBin < 32:
            shifter_operand = Rm << RsBin
            shifter_carry_out = BinStr(Rm)[32 - RsBin]
        elif RsBin == 32:
            shift_operand = 0
            shifter_carry_out = BinStr(Rm)[0]
        else:
            shifter_operand = 0
            shifter_carry_out = 0
        return shifter_operand
    else:
        print 'shift_lsl ERROR'
        return 0

def _shift_lsr(shift_operand, post_state):
    global shifter_carry_out
    Rm = get_value(shift_operand[0].strip(','), post_state)
    if check_imm(shift_operand[2]):
        shift_imm = int(shift_operand[2][1:], 16)
        if shift_imm == 0:
            shifter_operand = 0
            shifter_carry_out = BinStr(Rm)[31]
        else:
            shifter_operand = Rm >> shift_imm
            shifter_carry_out = BinStr(Rm)[shift_imm - 1]
        return shifter_operand
    elif check_reg(shift_operand[2]):
        Rs = get_value(shift_operand[2], post_state)
        RsBin = int(BinStr(Rs)[7:0], 2)
        if RsBin == 0:
            shifter_operand = Rm
            shifter_carry_out = post_state[1]['C']
        elif RsBin < 32:
            shifter_operand = Rm >> RsBin
            shifter_carry_out = BinStr(Rm)[RsBin - 1]
        elif RsBin == 32:
            shift_operand = 0
            shifter_carry_out = BinStr(Rm)[31]
        else:
            shifter_operand = 0
            shifter_carry_out = 0
        return shifter_operand
    else:
        print 'shift_lsr ERROR'
        return 0

def _shift_asr(shift_operand, post_state):
    global shifter_carry_out
    Rm = get_value(shift_operand[0].strip(','), post_state)
    if check_imm(shift_operand[2]):
        shift_imm = int(shift_operand[2][1:], 16)
        if shift_imm == 0:
            if int(BinStr(Rm)[31], 2) == 0:
                shifter_operand = 0
                shifter_carry_out = BinStr(Rm)[31]
            else:
                shifter_operand = 0xffffffff
                shifter_carry_out = BinStr(Rm)[31]
        else:
            shifter_operand = asr(Rm, shift_imm)
            shifter_carry_out = BinStr(Rm)[shift_imm - 1]
        return shifter_operand
    elif check_reg(shift_operand[2]):
        Rs = get_value(shift_operand[2], post_state)
        RsBin = int(BinStr(Rs)[7:0], 2)
        if RsBin == 0:
            shifter_operand = Rm
            shifter_carry_out = post_state[1]['C']
        elif RsBin < 32:
            shifter_operand = asr(Rm, RsBin)
            shifter_carry_out = BinStr(Rm)[RsBin - 1]
        elif RsBin >= 32:
            if int(BinStr(Rm)[31], 2) == 0:
                shift_operand = 0
                shifter_carry_out = BinStr(Rm)[31]
            else:
                shifter_operand = 0xffffffff
                shifter_carry_out = BinStr(Rm)[31]
        return shifter_operand
    else:
        print 'shift_lsr ERROR'
        return 0

def _shift_ror(shift_operand, post_state):
    global shifter_carry_out
    Rm = get_value(shift_operand[0].strip(','), post_state)
    if check_imm(shift_operand[2]):
        shift_imm = int(shift_operand[2][1:], 16)
        if shift_imm == 0:
            shifter_operand = post_state[1]['C'] << 31 | Rm >> 1
            shifter_carry_out = BinStr(Rm)[0]
        else:
            shifter_operand = cycle_shift(Rm, shift_imm)
            shifter_carry_out = BinStr(Rm)[shift_imm - 1]
        return shifter_operand
    elif check_reg(shift_operand[2]):
        Rs = get_value(shift_operand[2], post_state)
        RsBin = int(BinStr(Rs)[4:0], 2)
        if int(BinStr(Rs)[7:0], 2) == 0:
            shifter_operand = Rm
            shifter_carry_out = post_state[1]['C']
        elif RsBin == 0:
            shifter_operand = Rm
            shifter_carry_out = BinStr(Rm)[31]
        else:
            shifter_operand = cycle_shift(Rm, RsBin)
            shifter_carry_out = BinStr(Rm)[RsBin -1]
        return shifter_operand
    else:
        print 'shift_ror ERROR'
        return 0

def _shift_rrx(shift_operand, post_state):
    global shifter_carry_out
    Rm = get_value(shift_operand[0].strip(','), post_state)
    shifter_operand = post_state[1]['C'] << 31 | Rm >> 1
    shifter_carry_out = BinStr(Rm)[0]
    return shifter_operand

def shift(asm, shift_operand, post_state):
    shift_operand = [s for item in shift_operand for s in item.split(',') if s !='']
    def _split_with(asm):
        res = asm
        if len(shift_operand) == 2:
            if '#' in asm[1]:
                res[1], tmp = asm[1].split('#')
                res.append(tmp)
                res[2] = '#' + res[2]
        return res
    shift_operand = _split_with(shift_operand)
    opt_len = len(shift_operand)
    shifter_operand = 0
    if opt_len == 1:
        # shift_operand_0 = norma_imm(shift_operand[0])
        if check_imm(shift_operand[0]):
            print shift_operand
            print 'asm: %s' %asm
            return _shift_imm(shift_operand[0], post_state)
        elif check_reg(shift_operand[0]):
            return _shift_rm(shift_operand[0], post_state)
        else:
            print 'shift_operand ERROR 1'
            print shift_operand
            print 'asm: %s' %asm
            return 0
    elif opt_len == 3:
        if shift_operand[1].upper() == 'LSL':
            return _shift_lsl(shift_operand, post_state)
        elif shift_operand[1].upper() == 'LSR':
            return _shift_lsr(shift_operand, post_state)
        elif shift_operand[1].upper() == 'ASR':
            return _shift_asr(shift_operand, post_state)
        elif shift_operand[1].upper() == 'ROR':
            return _shift_ror(shift_operand, post_state)
        else:
            print 'shift_operand ERROR 2'
            print shift_operand
            print 'asm: %s' %asm
            return 0
    elif opt_len == 2:
        if shift_operand[1].upper() == 'RRX':
            return _shift_rrx(shift_operand, post_state)
        else:
            print 'shift_operand ERROR 3'
            print shift_operand
            print 'asm: %s' %asm
            return 0
    else:
        print 'shift_operand ERROR 4'
        print shift_operand
        return 0

def mov(asm, post_state):
    # Move
    # MOV{<cond>}{S} <Rd>, <shift_operand>
    # _asm = asm
    # _asm = [item for item in _asm.split(' ') if item != '']
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    Rd = _asm[1].strip(',')
    shift_operand = _asm[2:]
    shift_operand = shift(asm, shift_operand, post_state)
    post_state[0][Rd] = shift_operand
    if S == 1 and Rd != R15:
        Rdtmp = post_state[0][Rd]
        handleNZ(Rdtmp, post_state)
        post_state[1]['C'] = shifter_carry_out


def mvn(asm, post_state):
    # Move Not
    # MVN{<cond>}{S} <Rd>, <shift_operand>
    # _asm = asm
    # _asm = [item for item in _asm.split(' ') if item != '']
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    Rd = _asm[1].strip(',')
    shift_operand = _asm[2:]
    shift_operand = shift(asm, shift_operand, post_state)
    # if check_reg(shift_operand):
    #     # pre_state[Rd] = shift_operand[1:]
    #     # tmp = int(shift_operand[1:], 16)
    #     tmp = shift_operand
    #     if tmp not in post_state[0]:
    #         post_state[0][tmp] = 0
    #         tmp = 0
    #     else:
    #         tmp = post_state[0][tmp]
    #     if len(_asm) > 3:
    #         tmp = shift(tmp, _asm[3], _asm[4])
    #     post_state[0][Rd] = 0xffffffff - tmp
    # else:
    #     post_state[0][Rd] = 0xffffffff - int(shift_operand[1:],16)
    if S == 1 and Rd != R15:
        Rdtmp = post_state[0][Rd]
        handleNZ(Rdtmp, post_state)
        post_state[1]['C'] = shifter_carry_out

def over_flow_from(Rn, opt, operand, size=32):
    # print 'over_flow_from called.'
    if opt == '+':
        RnBin = BinStr(Rn, size)
        operandBin = BinStr(operand, size)
        ResBin = BinStr(Rn + operand, size)
        if RnBin.sf == operandBin.sf and RnBin.sf != ResBin.sf:
            # print 'return + 1'
            return 1
        else:
            return 0
    elif opt == '-':
        RnBin = BinStr(Rn, size)
        operandBin = BinStr(operand, size)
        ResBin = BinStr(Rn - operand, size)
        if RnBin.sf != operandBin.sf and RnBin.sf != ResBin.sf:
            return 1
        else:
            return 0
    else:
        return None

def carry_from(Rn, operand, size=32):
    RnBin = BinStr(Rn, size)
    operandBin = BinStr(operand, size)
    if int(RnBin.str, 2) + int(operandBin.str, 2) >= 2**size:
        return 1
    else:
        return 0

def borrow_from(Rn, operand, size=32):
    RnBin = BinStr(Rn, size)
    operandBin = BinStr(operand, size)
    if int(RnBin.str, 2) < int(operandBin.str, 2):
        return 1
    else:
        return 0


def handleNZ(operand, post_state):
    # print('handleNZ called.')
    alu_out = BinStr(operand) if type(operand) !=BinStr else operand
    post_state[1]['N'] = alu_out[alu_out.size-1]
    post_state[1]['Z'] = 1 if alu_out == 0 else 0

def get_value(reg, post_state):
    # print reg
    if reg not in post_state[0]:
        post_state[0][reg] = 0
        return 0
    else:
        return post_state[0][reg]

def get_asm(asm):
    _asm = asm
    _asm = [item for item in _asm.split(' ') if item != '']
    return _asm


def arithmetic_operation(asm, opt, post_state):
    # _asm = asm
    # _asm = [item for item in _asm.split(' ') if item != '']
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    Rd = _asm[1].strip(',')
    Rn = _asm[2].strip(',')
    if Rn not in post_state[0]:
        post_state[0][Rn] = 0
        Rn = 0
    else:
        Rn = post_state[0][Rn]
    shift_operand = _asm[3:]
    shift_operand = shift(asm, shift_operand, post_state)
    # if check_reg(shift_operand):
    #     tmp = shift_operand
    #     if tmp not in post_state[0]:
    #         post_state[0][tmp] = 0
    #         tmp = 0
    #     else:
    #         tmp = post_state[0][tmp]
    #     if len(_asm) > 4:
    #         tmp = shift(tmp, _asm[4], _asm[5])
    #     # post_state[0][Rd] = Rn + tmp
    #     post_state[0][Rd] = opt(S, Rd, Rn, tmp, post_state)
    # else:
    #     shift_operand = int(shift_operand[1:], 16)
    post_state[0][Rd] = opt(S, Rd, Rn,shift_operand, post_state)


def add(asm, post_state):
    # Add
    # ADD{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _add(S, Rd, Rn, shift_operand, post_state):
        res = Rn + shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = carry_from(Rn, shift_operand)
            post_state[1]['V'] = over_flow_from(Rn, '+', shift_operand)
        return res
    arithmetic_operation(asm, _add, post_state)

def sub(asm, post_state):
    # Subtract
    # SUB{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _sub(S, Rd, Rn, shift_operand, post_state):
        res = Rn - shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = 1 - borrow_from(Rn, shift_operand)
            post_state[1]['V'] = over_flow_from(Rn, '-', shift_operand)
        return res
    arithmetic_operation(asm, _sub, post_state)


def rsb(asm, post_state):
    # Reverse Subtract
    # RSB{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _rsb(S, Rd, Rn, shift_operand, post_state):
        res = shift_operand - Rn
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = 1 - borrow_from(shift_operand, Rn)
            post_state[1]['V'] = over_flow_from(shift_operand, '-', Rn)
        return res
    arithmetic_operation(asm, _rsb, post_state)


def adc(asm, post_state):
    # Add with Carry
    # ADC{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _adc(S, Rd, Rn, shift_operand, post_state):
        c_flag = post_state[1]['C']
        res = Rn + shift_operand + c_flag
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = carry_from(Rn, shift_operand + c_flag)
            post_state[1]['V'] = over_flow_from(Rn, '+', shift_operand + c_flag)
        return res
    arithmetic_operation(asm, _adc, post_state)




def sbc(asm, post_state):
    # Subtract with Carry
    # SBC{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _sbc(S, Rd, Rn, shift_operand, post_state):
        not_c_flag = 1 - post_state[1]['C']
        res = Rn - shift_operand - not_c_flag
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = 1 - borrow_from(Rn, shift_operand - not_c_flag)
            post_state[1]['V'] = over_flow_from(Rn, '-', shift_operand - not_c_flag)
        return res
    arithmetic_operation(asm, _sbc, post_state)


def rsc(asm, post_state):
    # Reverse Subtract with Carry
    # RSC{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _rsc(S, Rd, Rn, shift_operand, post_state):
        not_c_flag = 1 - post_state[1]['C']
        res = shift_operand - Rn - not_c_flag
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = 1- borrow_from(shift_operand, Rn - not_c_flag)
            post_state[1]['V'] = over_flow_from(shift_operand, '-', Rn - not_c_flag)
        return res
    arithmetic_operation(asm, _rsc, post_state)

def in_and(asm, post_state):
    # And
    # AND{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _in_and(S, Rd, Rn, shift_operand, post_state):
        res = Rn & shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = shifter_carry_out
        return res
    arithmetic_operation(asm, _in_and, post_state)

def orr(asm, post_state):
    # Logical OR
    # ORR{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _orr(S, Rd, Rn, shift_operand, post_state):
        res = Rn | shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = shifter_carry_out
        return res
    arithmetic_operation(asm, _orr, post_state)


def eor(asm, post_state):
    # Exclusive OR
    # EOR{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _eor(S, Rd, Rn, shift_operand, post_state):
        res = Rn ^ shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = shifter_carry_out
        return res
    arithmetic_operation(asm, _eor, post_state)


def bic(asm, post_state):
    # Bit Clear
    # BIC{<cond>}{S} <Rd>, <Rn>, <shift_operand>
    def _bic(S, Rd, Rn, shift_operand, post_state):
        shift_operand = 0xff - shift_operand
        res = Rn & shift_operand
        if S == 1 and Rd != R15:
            handleNZ(res, post_state)
            post_state[1]['C'] = shifter_carry_out
        return res
    arithmetic_operation(asm, _bic, post_state)

def logic_operation(asm, opt, post_state):
    # _asm = asm
    # _asm = [item for item in _asm.split(' ') if item != '']
    _asm = get_asm(asm)
    Rn = _asm[1].strip(',')
    # Rn = _asm[2].strip(',')
    if Rn not in post_state[0]:
        post_state[0][Rn] = 0
        Rn = 0
    else:
        Rn = post_state[0][Rn]
    shift_operand = _asm[2:]
    shift_operand = shift(asm, shift_operand, post_state)
    # if check_reg(shift_operand):
    #     tmp = shift_operand
    #     if tmp not in post_state[0]:
    #         post_state[0][tmp] = 0
    #         tmp = 0
    #     else:
    #         tmp = post_state[0][tmp]
    #     if len(_asm) > 4:
    #         tmp = shift(tmp, _asm[4], _asm[5])
    #     # post_state[0][Rd] = Rn + tmp
    #     opt(Rn, tmp, post_state)
    #     # pass
    # else:
    #     shift_operand = int(shift_operand[1:], 16)
    #     opt(Rn,shift_operand, post_state)
    opt(Rn, shift_operand, post_state)

def cmp(asm, post_state):
    # Compare
    # CMP{<cond>} <Rn>, <shift_operand>

    def _cmp(Rn, shift_operand, post_state):
        handleNZ(Rn-shift_operand, post_state)
        post_state[1]['C'] = 1 - borrow_from(Rn, shift_operand)
        post_state[1]['V'] = over_flow_from(Rn, '-', shift_operand)

    logic_operation(asm, _cmp, post_state)
    # pass

def cmn(asm, post_state):
    # Compare Negative
    # CMN{<cond>} <Rn>, <shift_operand>

    def _cmn(Rn, shift_operand, post_state):
        handleNZ(Rn+shift_operand, post_state)
        post_state[1]['C'] = carry_from(Rn, shift_operand)
        post_state[1]['V'] = over_flow_from(Rn, '+', shift_operand)

    logic_operation(asm, _cmn, post_state)
    # pass

def tst(asm, post_state):
    # Test
    # TST{<cond>} <Rn>, <shift_operand>

    def _tst(Rn, shift_operand):
        handleNZ(Rn & shift_operand, post_state)
        post_state[1]['C'] = shifter_carry_out #TODO shifter_carry_out具体定义

    logic_operation(asm, _tst, post_state)
    # pass

def teq(asm, post_state):
    # Test Equivalence
    # TEQ{<cond>} <Rn>, <shift_operand>

    def _teq(Rn, shift_operand):
        handleNZ(Rn ^ shift_operand, post_state)
        post_state[1]['C'] = shifter_carry_out

    logic_operation(asm, _teq, post_state)
    # pass


def mul(asm, post_state):
    # Multiply
    # MUL{<cond>}{S} <Rd>, <Rm>, <Rs>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    Rd = _asm[1].strip(',')
    Rm = _asm[2].strip(',')
    Rs = _asm[3]
    Rm = get_value(Rm, post_state)
    Rs = get_value(Rs, post_state)
    post_state[0][Rd] = Rm * Rs
    if S:
        handleNZ(Rm * Rs, post_state)
    # pass

def mla(asm, post_state):
    # Multiply Accumulate
    # MLA{<cond>}{S} <Rd>, <Rm>, <Rs>, <Rn>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    Rd = _asm[1].strip(',')
    Rm = get_value(_asm[2].strip(','), post_state)
    Rs = get_value(_asm[3].strip(','), post_state)
    Rn = get_value(_asm[4], post_state)
    post_state[0][Rd] = Rm * Rs + Rn
    if S:
        handleNZ(Rm*Rs+Rn, post_state)

    # pass

def umull(asm, post_state):
    # Unsigned Multiply Long
    # UMULL{<cond>}{S} <RdLo>, <RdHi>, <Rm>, <Rs>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    RdLo = _asm[1].strip(',')
    RdHi = _asm[2].strip(',')
    Rm = get_value(_asm[3].strip(','), post_state)
    Rs = get_value(_asm[4], post_state)

    RdBin = BinStr(Rm*Rs, 64)
    # Unsigned multiplication
    post_state[0][RdHi] = int(RdBin[63:32], 2)
    post_state[0][RdLo] = int(RdBin[31:0], 2)
    if S:
        handleNZ(RdBin, post_state)
    # pass

def umlal(asm, post_state):
    # Unsigned Multiply Accumulate Long
    # UMLAL{<cond>}{S} <RdLo>, <RdHi>, <Rm>, <Rs>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    RdLo = _asm[1].strip(',')
    RdHi = _asm[2].strip(',')
    Rm = get_value(_asm[3].strip(','), post_state)
    Rs = get_value(_asm[4], post_state)

    Rdtmp = BinStr(Rm*Rs, 64)
    # Unsigned multiplication
    post_state[0][RdLo] = int(Rdtmp[31:0], 2) + post_state[0][RdLo]
    post_state[0][RdHi] = int(Rdtmp[63:32], 2) + post_state[0][RdHi] +\
                        carry_from(int(Rdtmp[31:0], 2), post_state[0][RdLo])
    if S:
        handleNZ(Rdtmp, post_state)

def smull(asm, post_state):
    # Signed Multiply Long
    # SMULL{<cond>}{S} <RdLo>, <RdHi>, <Rm>, <Rs>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    RdLo = _asm[1].strip(',')
    RdHi = _asm[2].strip(',')
    Rm = get_value(_asm[3].strip(','), post_state)
    Rs = get_value(_asm[4], post_state)

    Rdtmp = BinStr(Rm*Rs, 64)
    # Singed multiplication
    post_state[0][RdHi] = int(Rdtmp[63:33], 2)
    post_state[0][RdLo] = int(Rdtmp[31:0], 2)
    if S:
        handleNZ(Rdtmp, post_state)

def smlal(asm, post_state):
    # Signed Multiply Accumulate Long
    # SMLAL{<cond>}{S} <RdLo>, <RdHi>, <Rm>, <Rs>
    _asm = get_asm(asm)
    S = 1 if _asm[0][-1].upper() == 'S' else 0
    RdLo = _asm[1].strip(',')
    RdHi = _asm[2].strip(',')
    Rm = get_value(_asm[3].strip(','), post_state)
    Rs = get_value(_asm[4], post_state)

    Rdtmp = BinStr(Rm*Rs, 64)
    # Signed multiplication
    post_state[0][RdLo] = int(Rdtmp[31:0], 2) + post_state[0][RdLo]
    post_state[0][RdHi] = int(Rdtmp[63:32], 2) + post_state[0][RdHi] +\
                        carry_from(int(Rdtmp[31:0], 2), post_state[0][RdLo])
    if S:
        handleNZ(Rdtmp, post_state)

R15 = 'R15'
shifter_carry_out = 0

execute_dic = {
    'mov':mov,
    'mvn':mvn,
    'add':add,
    'sub':sub,
    'rsb':rsb,
    'adc':adc,
    'sbc':sbc,
    'rsc':rsc,
    'and':in_and,
    'orr':orr,
    'eor':eor,
    'bic':bic,
    'cmp':cmp,
    'cmn':cmn,
    'tst':tst,
    'teq':teq,
    'mul':mul,
    'mla':mla,
    'umull':umull,
    'umlal':umlal,
    'smull':smull,
    'smlal':smlal,
}
