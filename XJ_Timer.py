#后来才发现Qt自带定时器的东西，但既然都写出来了就留着了（毕竟这玩意儿写了一天，除非真的用不了要不然不会删的）

from time import sleep#休眠
from time import time#获取时间戳
from threading import Thread#弄个子线程去定时执行任务
from threading import Lock#线程锁
from threading import currentThread#获取当前线程

import traceback#用于打印异常的


__all__=['XJ_Timer']

class XJ_Timer:#定时器。
    #本来定时逻辑是耦合到XJ_ScreenMonitor(屏幕监控器)里头的，但想着属实不合适就硬着去分离出来这个东西。（还好抽离了出来。现在回头看了下那屏幕监控器的代码，不敢动不敢动
    #只不过后来也发现，其实pyqt是自带了定时器这个玩意儿的，每个控件(或者说是QObject对象)都有startTimer方法，没必要自己做个不靠谱的定时器出来
    #只不过既然把这玩意儿写出来了那就留着吧，毕竟这定时器仅依赖py自带的模块(threading,time)
    def __init__(self,timeOverFunc=lambda:print("本轮计时结束"),looping=False):#looping为循环计时，为真时会不停地计时(效果就是周期调用timeOverFunc
        self.__timeOverFunc=timeOverFunc
        self.__looping=looping

        self.__interval=1#定时时间
        self.__sleep=0#休眠时间
        self.__timeStamp=0#时间戳
        self.__threads=set()#当前执行监控的线程
        self.__lock_run=Lock()#线程锁，跑关键内容时上锁
        self.__lock_clear=Lock()#线程锁，清除self.__thread时上锁
        self.__loopStrict=False#严格计时，每轮调用timeOverFunc的时间间隔为self.__interval。如果不是严格计时的话每轮都在timeOverFunc执行完毕后才进行下一轮计时

    def IsRunning(self):#判断是否计时中
        return bool(len(self.__threads))

    def SetLooping(self,looping):#设置循环计时
        self.__looping=looping

    def SetLoopStrict(self,flag):#设置严格计时
        self.__loopStrict=flag

    def SetLoopInterval(self,interval):#设置时间间隔
        self.__interval=interval
        self.__sleep=interval

    def SetTimeOverFunc(self,timeOverFunc):#设置时间结束时的回调函数
        self.__timeOverFunc=timeOverFunc

    def GetTimeOverFunc(self):#获取回调函数
        return self.__timeOverFunc

    def Start(self):#开始计时。如果在计时中的话那么将直接重置计时
        self.__sleep=self.__interval
        self.__timeStamp=time()#更新时间戳
        Thread(target=self.__ThreadFunc).start()#开始计时

    def Pause(self):#暂停计时
        if(len(self.__threads)>0):#仅在计时的时候执行
            self.__sleep=self.__sleep-(time()-self.__timeStamp)#计算剩余的休眠时间
            self.__threads.clear()

    def Continue(self,extraInterval=0):#继续计时，如果正在计时中的话那么该调用不生效。(interval为额外的时间，用于延缓/提前本轮的计时
        if(len(self.__threads)==0):#仅在不计时的时候执行
            if(self.__sleep==0):
                self.__sleep=self.__interval
            self.__sleep=self.__sleep+extraInterval
            self.__timeStamp=time()#更新时间戳
            Thread(target=self.__ThreadFunc).start()#开始计时


    def __ThreadFunc(self):#给线程跑的
        self.__threads.add(currentThread())#立马记录
        if(self.__sleep>0):#开始睡大觉
            sleep(self.__sleep)
        if(currentThread() not in self.__threads):#睡醒时发现被抛弃
            return
        
        if(self.__loopStrict):
            self.__NewThread()
            self.__CallFunc()
        else:
            self.__CallFunc()
            self.__NewThread()
        try:
            self.__threads.remove(currentThread())
        except:
            pass

    def __NewThread(self):#供__treadFunc使用。创建新线程
        if(self.__looping):#如果开着循环计时那么就整个新线程(子子孙孙无穷尽，一代传一代)
            stamp=time()
            self.__lock_run.acquire()#加锁
            if(self.__loopStrict):#如果是严格计时的话，就修正下一次休眠的时间
                self.__sleep=self.__interval-(stamp-self.__timeStamp-self.__sleep)
                if(self.__sleep<0):
                    self.__sleep=0
            else:
                self.__sleep=self.__interval
            self.__timeStamp=stamp#更新时间戳
            if(currentThread() in self.__threads):#如果当前线程没被抛弃，就开启新线程
                Thread(target=self.__ThreadFunc).start()#新线程
            self.__lock_run.release()#解锁
    def __CallFunc(self):#供__treadFunc使用。调用timeOverFunc
        try:#try-catch防止回调函数翻车
            self.__timeOverFunc()#调用回调函数
        except Exception:
            self.__lock_run.acquire()#加锁
            self.__threads.clear()#翻车了就赶紧停掉计时器
#            if(currentThread() in self.__threads):#防止多次打印异常（虽然带有异常的函数可能被多次执行...
#                print(traceback.format_exc())
            print(traceback.format_exc())
            self.__lock_run.release()#解锁

        

if __name__=="__main__":
    timer=XJ_Timer(looping=True)
    timer.SetTimeOverFunc(lambda:print("本轮计时结束") or sleep(1.5))
    timer.SetLoopStrict(True)
    print("【开始】")
    timer.Start()

    sleep(1.3)
    print("【加时1秒】")
    timer.Pause()
    timer.Continue(1)
    sleep(2)
    print("【暂停】")
    timer.Pause()

