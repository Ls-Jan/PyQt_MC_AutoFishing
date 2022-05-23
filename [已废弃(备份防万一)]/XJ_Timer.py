
from time import sleep#休眠
from time import time#获取时间戳
from threading import Thread#弄个子线程去定时执行任务
from threading import Lock#线程锁
from threading import currentThread#获取当前线程

__all__=['XJ_Timer']

class XJ_Timer:#定时器。本来定时逻辑是耦合到XJ_ScreenMonitor(屏幕监控器)里头的，但想着属实不合适就硬着去分离出来这个东西
    def __init__(self,timeOverFunc=lambda:print("本轮计时结束"),loop=False):#loop为循环计时，为真时会不停地计时(效果就是周期调用timeOverFunc
        self.__timeOverFunc=timeOverFunc
        self.__loop=loop

        self.__interval=1#定时时间
        self.__sleep=0#休眠时间
        self.__timeStamp=0#时间戳
        self.__thread=None#当前执行监控的线程
        self.__lock_run=Lock()#线程锁，跑关键内容时上锁
        self.__lock_clear=Lock()#线程锁，清除self.__thread时上锁
        
    def IsRunning(self):#判断是否计时中
        return self.__thread!=None

    def SetLoop(self,loop):#设置循环计时
        self.__loop=loop

    def SetLoopInterval(self,interval):#设置时间间隔
        self.__interval=interval
        self.__sleep=interval

    def SetTimeOverFunc(self,timeOverFunc):#设置时间结束时的回调函数
        self.__timeOverFunc=timeOverFunc


    def Start(self):#开始计时。如果在计时中的话那么将直接重置计时
        self.__sleep=self.__interval
        self.__timeStamp=time()#更新时间戳
        Thread(target=self.__ThreadFunc).start()#开始计时

    def Pause(self):#暂停计时
        if(self.__thread!=None):#仅在计时的时候执行
            self.__sleep=self.__sleep-(time()-self.__timeStamp)#计算剩余的休眠时间
            self.__thread=None

    def Continue(self,extraInterval=0):#继续计时，如果正在计时中的话那么该调用不生效。(interval为额外的时间，用于延缓/提前本轮的计时
        if(self.__thread==None):#仅在不计时的时候执行
            if(self.__sleep==0):
                self.__sleep=self.__interval
            self.__sleep=self.__sleep+extraInterval
            self.__timeStamp=time()#更新时间戳
            Thread(target=self.__ThreadFunc).start()#开始计时


    def __ThreadFunc(self):#给线程跑的
        self.__thread=currentThread()#立刻记录当前线程
        while(True):#因为py没有do-while，所以这代码显得有点下饭。当self.__loop为假时退出循环
            if(self.__sleep>0):#开始睡大觉
                sleep(self.__sleep)
            if(currentThread()!=self.__thread):#睡醒时发现被抛弃
                break

            self.__lock_run.acquire()#上锁
            try:#try-catch防止回调函数翻车
                self.__timeOverFunc()#调用回调函数
                stamp=time()
                self.__sleep=self.__interval-(stamp-self.__timeStamp-self.__sleep)#修正下一次休眠的时间
                self.__timeStamp=stamp#更新时间戳
            except Exception as exception:
                pass
            self.__lock_run.release()#解锁
            if(locals().get('exception')!=None):#终止循环(都跑出异常了肯定直接停掉它
                break

            if(self.__loop==False):
                break

        self.__lock_clear.acquire()#上锁防翻车
        if(self.__thread==currentThread()):
            self.__thread=None
        self.__lock_clear.release()#解锁

if __name__=="__main__":
    timer=XJ_Timer(loop=True)
    timer.Start()

    sleep(1.1)
    print("【加时2秒】")
    timer.Pause()
    timer.Continue(2)



