#
#Copyright (c) 2018 Jie Zheng
#

class e3_exception(Exception):
    def __init__(self,exp=None):
        self.explanation=exp
    def __str__(self):
        return repr(self.explanation)

