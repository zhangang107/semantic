# -*- coding:UTF-8 -*-
# @Author: zhangang <zhangang>
# @Date:   2017-11-20T16:24:15+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: binstr.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T16:11:30+08:00
# @Copyright: Copyright by USTC

from collections import deque

class BinStr(object):
    """docstring CreateBinStr."""
    def __init__(self, num, size=32):
        self.num = num
        self.size = size
        self.error = False
        self.str = self.__createbinstr(self.num)

    def __createbinstr(self, num):
        # self.sf = 0
        # if num < 0:
        #     num = deque(bin(num)[3:]) if type(num)==int else deque(num)
        #     n_flag = True
        # else:
        #     num = deque(bin(num)[2:]) if type(num)==int else deque(num)
        if type(num) == int:
            if num < 0:
                num = 2 ** self.size -abs(num)
                num = deque(bin(num)[2:])
            else:
                num = deque(bin(num)[2:])
        else:
            num = deque(num)
        _length = len(num)
        # print _length
        if _length > self.size :
            print 'ERROR: num out of range or step out %d' % self.size
            self.error = True
            return ''
        for i in range(self.size-_length):
            num.appendleft('0')
        # if self.sf:
        #     num.appendleft('1')
        self.sf = int(num[0])
        return ''.join([i for i in num])

    def __len__(self):
        return self.size

    def __repr__(self):
        if self.error:
            print "size error"
        return self.str

    def __getitem__(self, key):
        return int(self.str[self.size-key-1],2)

    def __invert__(self):
        size = self.size - 1
        num_tmp = 0
        while size >= 0:
            num_tmp += 2 ** size
            size -= 1
        num = num_tmp - self.num
        return self.__createbinstr(num)

    def __eq__(self, num):
        return int(self.str, 2) == num

    def __getslice__(self, index1, index2):
        return self.str[self.size-index1-1:self.size-index2 + 1]
