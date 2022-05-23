#测试多线程的样例代码
#看来1w休眠线程都不会对性能造成过分影响呢

from time import sleep#休眠
from time import time#记录时间戳
from threading import Thread#弄个子线程去定时执行任务


def Func(num):
    print('{:6}'.format(num))
    stamp=time()
    sleep(10)
    print('{:6}：   {:<}'.format(num,round(time()-stamp,3)))

if __name__=="__main__":
    for i in range(10000):
        Thread(target=Func,args=(i,)).start()

    sleep(1)
    print('\n\n')
    Func(99999)





