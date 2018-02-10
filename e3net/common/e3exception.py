#
#Copyright (c) 2018 Jie Zheng
#
E3_EXCEPTION_IN_USE=1
E3_EXCEPTION_NOT_FOUND=2
E3_EXCEPTION_INVALID_ARGUMENT=3
E3_EXCEPTION_OUT_OF_RESOURCE=4
E3_EXCEPTION_NOT_SUPPORT=5
E3_EXCEPTION_BE_PRESENT=6
E3_EXCEPTION_NOT_SUCCESSFUL=7
E3_EXCEPTION_NOT_READY=8

err_invt={
    E3_EXCEPTION_IN_USE:'E3_EXCEPTION_IN_USE',
    E3_EXCEPTION_NOT_FOUND:'E3_EXCEPTION_NOT_FOUND',
    E3_EXCEPTION_INVALID_ARGUMENT:'E3_EXCEPTION_INVALID_ARGUMENT',
    E3_EXCEPTION_OUT_OF_RESOURCE:'E3_EXCEPTION_OUT_OF_RESOURCE',
    E3_EXCEPTION_NOT_SUPPORT:'E3_EXCEPTION_NOT_SUPPORT',
    E3_EXCEPTION_BE_PRESENT:'E3_EXCEPTION_BE_PRESENT',
    E3_EXCEPTION_NOT_SUCCESSFUL:'E3_EXCEPTION_NOT_SUCCESSFUL',
    E3_EXCEPTION_NOT_READY:'E3_EXCEPTION_NOT_READY'
}

class e3_exception(Exception):
    def __init__(self,exception_type,exp=None):
        self.explanation=exp
        self.exception_type=exception_type

    def __str__(self):
        return repr('%s:%s'%(err_invt[self.exception_type],
            self.explanation))


if __name__=='__main__':
    try:
        raise e3_exception(E3_EXCEPTION_OUT_OF_RESOURCE,'dsd')
    except Exception as e:
        print(isinstance(e,e3_exception))
        print(e.exception_type)
