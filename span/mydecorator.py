# @Author: zhangang <zhangang>
# @Date:   2017-12-01T14:38:44+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: decorator.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-05T10:24:33+08:00
# @Copyright: Copyright by USTC

from functools import wraps
import time

def timefn(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print("@timefn:" + fn.func_name + " took " + str(t2 - t1) + "seconds")
        return result
    return measure_time
