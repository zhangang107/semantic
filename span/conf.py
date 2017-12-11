# @Author: zhangang <zhangang>
# @Date:   2017-12-11T14:12:38+08:00
# @Email:  zhanganguc@gmail.com
# @Filename: conf.py
# @Last modified by:   zhangang
# @Last modified time: 2017-12-11T14:17:53+08:00
# @Copyright: Copyright by USTC

import ConfigParser
import os

cf = ConfigParser.ConfigParser()
cf.read("test.conf")

# secs = cf.sections()
# print 'sections:', secs, type(secs)
#
# opts = cf.options('sqlite3')
# print 'options:', opts, type(opts)
#
# kvs = cf.items('sqlite3')
# print 'sqlite3:', kvs

db_name = cf.get('sqlite3', 'db_name')
# print db_name
