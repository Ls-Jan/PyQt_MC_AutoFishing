
from XJ_Timer import XJ_Timer
from time import time
from time import sleep
from threading import Thread
from threading import currentThread

__all__=['XJ_Timer_CountDown']


class XJ_Timer_CountDown:#倒计时器
    def __init__(self,timeHintFunc=lambda:print("计时中..."),timeOverFunc=lambda:print("倒计时结束")):
        self.__timer=XJ_Timer(self.__ThreadFunc,True)
        self.__timer.SetLoopStrict(False)#非严格计时

        self.__timeHintFunc=timeHintFunc
        self.__timeOverFunc=timeOverFunc
        self.__timeStamp=0#时间戳
        self.__countDown=0#倒计时时间
        self.__interval=1#调用提示的时间间隔
        self.__thread=None#防睡醒时易主的情况
        
    def Start(self,countDown):#开始倒计时
        timer=self.__timer
        timer.Pause()

        self.__thread=None
        self.__countDown=countDown
        self.__timeStamp=time()#记录时间戳
        if(countDown<self.__interval):#如果倒计时压根不够长
            Thread(target=self.__ThreadFunc).start()
        else:
            Thread(target=self.__timeHintFunc).start()#打印一下时间(防被阻塞)
            timer.Start()

    def Stop(self):#提前结束倒计时
        self.__countDown=0
        self.__thread=None
        self.__timer.Pause()

    def SetTimeHintFunc(self,timeHintFunc):#设置倒计时提示函数
        self.__timeHintFunc=timeHintFunc
    def SetTimeOverFunc(self,timeOverFunc):#设置时间结束时的回调函数
        self.__timeOverFunc=timeOverFunc
    def SetInterval(self,interval):#设置提示的时间间隔
        if(interval>0):
            self.__interval=interval
    def GetRemainingTime(self):#获取倒计时的剩余时间(如果倒计时不在运行的话该值为0
        t=self.__countDown-(time()-self.__timeStamp)
        return t if t>0 else 0

    def __ThreadFunc(self):#给定时器跑的
        reTime=self.GetRemainingTime()
        self.__timeHintFunc()
        if(reTime<self.__interval):#剩下的一点时间就直接睡过去
            timer=self.__timer
            timer.Pause()
            self.__thread=currentThread()
            sleep(reTime)
            if(self.__thread==currentThread()):#如果睡醒时倒计时器没发生变化的话(因为倒计时器一旦调用了Start或是Stop，self.__thread都会发生变化，以此作为变化的判断依据
                self.__timeOverFunc()


if __name__=="__main__":
    timer=XJ_Timer_CountDown()
    timer.SetTimeHintFunc(lambda:print('剩余时间：',round(timer.GetRemainingTime(),3)))

    print("【开始】")
    timer.Start(2.5)
    timer.Start(0.5)
    timer.Stop()



