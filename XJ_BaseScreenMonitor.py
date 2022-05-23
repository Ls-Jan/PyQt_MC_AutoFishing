

import sys
from time import sleep
from PIL.ImageGrab import grab#获取屏幕截图：https://www.pythonthree.com/take-screenshots-using-python/
from threading import Lock#线程锁

from PyQt5.QtGui import QTextCursor,QTextCharFormat,QColor
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QHBoxLayout,QVBoxLayout,QLabel
from PyQt5.QtCore import Qt,pyqtSignal

from XJ_Timer import XJ_Timer#定时器
from XJ_Timer_CountDown import XJ_Timer_CountDown#倒计时器
from XJ_ScreenClipper import XJ_ScreenClipper#选区器
from XJ_UsefulWidgets import XJ_TextEdit#文本框
from XJ_UsefulWidgets import XJ_NumInput#数值框

__all__=['XJ_BaseScreenMonitor']



class XJ_BaseScreenMonitor(QLabel):#屏幕监控基类，做好了简单的东西，不做死它是因为这要留有一定的修改空间，提高可重用率
    __signal_appendText=pyqtSignal()#使用了奇怪的方法绕开了python子线程(threading.Thread)修改QTextEdit出错的问题，虽然感觉本质上还是用了Qt的子线程(QThread)但不想改了。只能说好孩子别乱学，这做法并不规范
    __signal_clearText=pyqtSignal()

    def __init__(self,parent=None):
        super().__init__(parent)

        self.__wid_output=XJ_TextEdit(self)#文本输出框
        self.__wid_fps=XJ_NumInput(self)#帧率
        self.__btn_clearOutput=QPushButton('清空',self)#清空输出文本
        self.__btn_clipper=QPushButton(' 选区 ',self)#创建选区
        self.__btn_test=QPushButton('  测试  ',self)#测试按钮(仅设置选区时显示)
        self.__btn_run=QPushButton('  运行  ',self)#运行按钮(仅设置选区时显示)
        self.__lb_fps=QLabel('时间间隔：',self)#帧率对应的label

        wids={}#保存所有组件到字典中
        for key in dir(self):
            k=[k for k in ['__wid','__btn','__lb'] if key.find(k)!=-1]
            if(len(k)>0):
                pst=key.find('__')
                wids[key[2+(pst):]]=eval('self.'+key)
        self.__wids=wids#所有组件的字典

        self.__screenClipper=XJ_ScreenClipper(self)#选区器
        self.__timer_running=XJ_Timer()#定时器
        self.__timer_countDown=XJ_Timer_CountDown()#倒计时器，用于点击“测试”和“运行”时有几秒钟的时间让用户做好准备

        self.__func_test=lambda pilImg:print('选区大小：'+str(pilImg.size),file=self,flush=True)#“测试”开始执行时每帧的回调函数
        self.__func_run=lambda pilImg:print('选区大小：'+str(pilImg.size),file=self,flush=True)#“运行”开始执行时每帧的回调函数

        self.__sheet_running=''#运行时按钮的样式表
        self.__sheet_normal=''#一般时按钮的样式表
        self.__output_prompt='<font color=#0080D0 ; size=4>>\n</font>'#文本框行首提示符
        self.__output_contextTag='<font color=#FFFF00 ; size=4>{}</font>'#文本框的输出文本的样式

        self.__btnStatus={self.__btn_clipper:False,self.__btn_test:False,self.__btn_run:False}#按钮状态(如果是运行中则为True
        self.__printCache=[]#供write和flush使用。(真麻烦
        self.__lock_output=Lock()#没啥用的线程锁。在输出文本时上锁
        self.__region=None#监控范围(四元组，作为grab的参数)

        self.__InitConfig()#进行进一步的初始化

    def __InitConfig(self):#进一步的初始化（单独抽离出来，仅仅为了好看+规范
        wid_output=self.__wid_output
        wid_fps=self.__wid_fps
        btn_clearOutput=self.__btn_clearOutput
        btn_clipper=self.__btn_clipper
        btn_run=self.__btn_run
        btn_test=self.__btn_test
        lb_fps=self.__lb_fps
        screenClipper=self.__screenClipper
        timer_R=self.__timer_running
        timer_CD=self.__timer_countDown

        #组件的独立设置
        wid_fps.SetValueRange(1,500)
        wid_fps.SetTextFormat(lambda num:str(round(num/100,2)).ljust(4,'0')+'s')
        wid_fps.SetValue(50)
        wid_fps.SetAlignment(Qt.AlignLeft)
        wid_output.setReadOnly(True)#设置为只读
        wid_output.document().setMaximumBlockCount(1000)#设置输出的最大行数
        timer_CD.SetInterval(1)
        timer_CD.SetTimeHintFunc(lambda:print('倒计时：'+str(round(self.__timer_countDown.GetRemainingTime(),1)),file=self,flush=True))
        timer_CD.SetTimeOverFunc(lambda:print('倒计时结束，开始运行！',file=self,flush=True) or self.__timer_running.Start())
        timer_R.SetLoopStrict(False)
        timer_R.SetLooping(True)
        timer_R.SetTimeOverFunc(self.__Func_Timer_Running)
        timer_R.SetLoopInterval(wid_fps.GetValue()/100)
        
        #设置回调函数
        btn_clearOutput.clicked.connect(self.__Func_Click_Clear)
        btn_clipper.clicked.connect(self.__Func_Click_Clipper)
        btn_test.clicked.connect(self.__Func_Click_Test)
        btn_run.clicked.connect(self.__Func_Click_Run)
        screenClipper.clipVisibleChanged.connect(self.__Func_ClipVisibleChanged)
        screenClipper.clipChanged.connect(self.__Func_ClipChanged)
        wid_fps.valueChanged.connect(lambda val:timer_R.SetLoopInterval(val/100))
        self.__signal_appendText.connect(self.__Func_AppendText)
        self.__signal_clearText.connect(self.__Func_ClearText)
        
        #隐藏俩按钮
        btn_run.hide()
        btn_test.hide()

        self.setFocusPolicy(Qt.ClickFocus|Qt.WheelFocus)#让控件可以获取焦点
#        self.setMaximumHeight(250)
        self.setMinimumWidth(600)
        self.setWindowOpacity(0.75)#窗口透明
        self.clear()#重置文本框内容

    def UseDefaultStyleSheet(self):#使用预置样式表
        #设置样式表
        self.__sheet_normal=\
        ''' 
            border-radius:5px ;
            background-color:rgb(0,255,128) ; 
            color:rgb(0,0,0) ; 
            font-size:23px ; 
            font-family:"黑体"
        '''
        self.__sheet_running=\
        '''
            border-radius:5px ;
            background-color:rgb(255,0,32) ;
            color:rgb(0,0,0) ;
            font-size:23px ;
            font-family:"黑体"
        '''
        self.__wid_fps.setStyleSheet(#设置fps
        '''
            color:#FF0000 ; 
        ''')
        self.__lb_fps.setStyleSheet(#设置fps-label
        '''
            color:#FFFFFF ;
            font-size:20px ;
            font-weight: bold ;
        ''')
        self.__btn_clearOutput.setStyleSheet(#设置清空按钮
        '''
            border-radius:5px ;
            border:1px solid rgb(255,64,255) ;
            color:rgb(255,0,255) ;
            font-size: 22px ;
        ''')
        self.__wid_output.verticalScrollBar().setStyleSheet(#滚动条样式表：https://blog.csdn.net/weixin_51965272/article/details/123965396
        '''
            QScrollBar:vertical{width:8px;background:transparent;}
            QScrollBar::handle:vertical{background:rgb(224,224,224); width:5px; border-radius:3px;}
            QScrollBar::up-arrow:vertical{border:none;}
            QScrollBar::sub-line:vertical{background:transparent;}
            QScrollBar::add-line:vertical{background:transparent;}
        ''')
        self.setStyleSheet(#设置所有组件背景为黑
        '''
            *{
                background-color:#080808 ; 
            }
            #XJ_BaseScreenMonitor{
                border:2px solid rgb(0,64,255) ;
            }
        ''')
        self.setObjectName('XJ_BaseScreenMonitor')
        self.__SetBtnStyle()

    def UseDefaultLayout(self):#使用预置布局
        if(self.layout()==None):#因为控件的布局一旦设置好就不可改。不知道Qt这么做的原因
            wid_output=self.__wid_output
            wid_fps=self.__wid_fps
            btn_clearOutput=self.__btn_clearOutput
            btn_clipper=self.__btn_clipper
            btn_run=self.__btn_run
            btn_test=self.__btn_test

            #把“清除”按钮放置在输出框的右下角
            widsLeft=QVBoxLayout()
            if(wid_output.layout()==None):
                hbox=QHBoxLayout(wid_output)
                vbox=QVBoxLayout()
                vbox.addStretch(1)
                vbox.addWidget(btn_clearOutput)
                hbox.addStretch(10)
                hbox.addLayout(vbox)
            widsLeft.addWidget(wid_output)

            #文本框右侧的组件盒
            widsRight=QVBoxLayout()

            #弄好fps数值框和clipper按钮，然后加进widsBox里头
            hbox=QHBoxLayout()
            hbox.addWidget(self.__lb_fps)
            hbox.addWidget(wid_fps,1)
            hbox.addStretch(10)
            widsRight.addLayout(hbox)
            hbox=QHBoxLayout()
            hbox.addWidget(btn_clipper)
            hbox.addStretch(1)
            widsRight.addLayout(hbox)

            #弄好test按钮和run按钮，然后加进widsBox里头
            hbox=QHBoxLayout()
            vbox=QVBoxLayout()
            vbox.addWidget(btn_test)
            vbox.addWidget(btn_run)
            hbox.addStretch(1)
            hbox.addLayout(vbox)
            widsRight.addStretch(1)
            widsRight.addLayout(hbox)

            mainBox=QHBoxLayout(self)
            mainBox.addLayout(widsLeft,5)
            mainBox.addLayout(widsRight,1)

    def GetWidgets(self):#返回所有组件，用于各种自定义。【按钮的click事件已占用，别更改其click的回调】
        return self.__wids.copy()

    def SetOutputPrompt(self,prompt):#设置文本框行首提示符。
        #格式为："<***> XXX </***>"。
        #XXX为提示符，
        #<***></***>懂的都懂，html标签
        self.__output_prompt=prompt

    def SetOuputContextTag(self,tag="<font color=#FF0000>{}</font>"):#设置文本框的输出文本的样式(有且仅有一个花括号，到时要用str.format进行设置的。
        #格式为："<***> {} </***>"。
        #{}不能多不能少，因为要用str.format函数，
        #<***></***>懂的都懂，html标签
        self.__output_contextTag=tag

    def SetBtnSheet_Running(self,sheet):#设置运行时按钮的样式表(按钮)
        self.__sheet_normal=sheet
        self.__SetBtnStyle()

    def SetBtnSheet_Normal(self,sheet):#设置一般时按钮的样式表(按钮)
        self.__sheet_running=sheet
        self.__SetBtnStyle()

    def SetFunc_Test(self,func=lambda pilImg:print('选区大小：'+str(pilImg.size),file=self,flush=True)):#设置“测试”开始执行时每帧的回调函数
        self.__func_test=func

    def SetFunc_Run(self,func=lambda pilImg:print('选区大小：'+str(pilImg.size),file=self,flush=True)):#设置“运行”开始执行时每帧的回调函数
        self.__func_run=func

    def write(self,text):#搞了这个函数。没错，到时可以print时指定输出的对象为本类对象
        self.__printCache.append(text)
    def flush(self):
        self.__signal_appendText.emit()
    def clear(self):
        self.__signal_clearText.emit()




    def __SetBtnStyle(self):#根据当前状态设置好按钮的样式
        for btn in self.__btnStatus:
            btn.setStyleSheet(self.__sheet_running if self.__btnStatus[btn] else self.__sheet_normal)

    def __Func_ClearText(self):#清空文本，占用事件__signal_clearText
        self.__wid_output.setText(self.__output_prompt)
    def __Func_AppendText(self):#添加文本，占用事件__signal_appendText
        #QTextEdit.append属实不好用

        self.__lock_output.acquire()
        cursor=self.__wid_output.textCursor()#光标
        cursor.movePosition(QTextCursor.End)#移到文末

        #因为，额，怎么说呢，例如print('123')，它实际上丢进字串缓存列表是这样的：['123','\n']，没错，'123'和'\n'是分开的，就不是很懂为什么会这样
        for line in [''.join(item) for item in zip(self.__printCache[0::2],self.__printCache[1::2])]:
            line.split()
            cursor.insertHtml(self.__output_contextTag.format(line))
            
            cursor.insertText('\n')
            cursor.insertHtml(self.__output_prompt)
        self.__printCache.clear()
        self.__wid_output.setTextCursor(cursor)#移动文本光标
        self.__lock_output.release()

    def __Func_ClipChanged(self):#选取发生变化时调用，用于对self.__region赋值
        rect=self.__screenClipper.GetClip()
        self.__region=[rect.left(),rect.top(),rect.right(),rect.bottom()]

    def __Func_ClipVisibleChanged(self):#选区显示/消失时调用，主要用于：控制“测试”、“运行”的显隐以及“选区”按钮的样式 ； 暂停定时器
        btn_clipper=self.__btn_clipper
        btn_run=self.__btn_run
        btn_test=self.__btn_test

        btnStatus=self.__btnStatus
        for btn in btnStatus:
            btnStatus[btn]=False
        if(self.__screenClipper.isVisible()):
            btn_run.show()
            btn_test.show()
            btnStatus[btn_clipper]=True
        else:
            btn_run.hide()
            btn_test.hide()
            self.__timer_countDown.Stop()#停下倒计时器
            self.__timer_running.Pause()#暂停定时器
        self.__SetBtnStyle()

    def __Func_Click_Clear(self):#点击了“清除”按钮
        self.clear()

    def __Func_Click_Clipper(self):#点击了“选区”按钮
        clipper=self.__screenClipper
        if(clipper.isVisible()):#如果可见那么就隐藏，反之显示
            clipper.hide()
        else:
            clipper.show()

    def __Func_Click_Test(self):#点击了“测试”按钮
        timer_R=self.__timer_running
        timer_CD=self.__timer_countDown

        btnStatus=self.__btnStatus
        btn_test=self.__btn_test
        btn_run=self.__btn_run

        #停下计时器
        timer_CD.Stop()
        timer_R.Pause()
        sleep(0.1)
        print('\n',file=self,flush=True)
        if(btnStatus[btn_test]):#正在运行中
            btnStatus[btn_test]=False
        else:#未运行
            btnStatus[btn_test]=True
            btnStatus[btn_run]=False
            timer_CD.Start(3)#三秒的倒计时
        self.__SetBtnStyle()

    def __Func_Click_Run(self):#点击了“运行”按钮
        timer_R=self.__timer_running
        timer_CD=self.__timer_countDown

        btnStatus=self.__btnStatus
        btn_test=self.__btn_test
        btn_run=self.__btn_run

        #停下计时器
        timer_CD.Stop()
        timer_R.Pause()
        sleep(0.1)
        print('\n',file=self,flush=True)
        if(btnStatus[btn_run]):#正在运行中
            btnStatus[btn_run]=False
        else:#未运行
            btnStatus[btn_run]=True
            btnStatus[btn_test]=False
            timer_CD.Start(3)#三秒的倒计时
        self.__SetBtnStyle()

    def __Func_Timer_Running(self):#供self.__timer_running运行的函数
        btnStatus=self.__btnStatus
        btn_test=self.__btn_test
        btn_run=self.__btn_run

        if(btnStatus[btn_test]):#运行的是“Test”
            self.__func_test(grab(self.__region))
        elif(btnStatus[btn_run]):#运行的是“Run”
            self.__func_run(grab(self.__region))

if __name__=='__main__':
    app = QApplication(sys.argv)

    sm= XJ_BaseScreenMonitor()
    sm.UseDefaultLayout()#使用预置好的布局
    sm.UseDefaultStyleSheet()#使用预置好的样式表
    sm.show()
    sm.resize(1000,600)

    sm.SetOutputPrompt('<font size=4 color=#00FFFF>></font>')#设置文本框行首提示符
    sm.SetOuputContextTag('<font size=2 color=#FF00FF>{}</font>')#设置文本框的输出文本的样式
    print('111',file=sm)
    print('2222222',file=sm)
    print('333333333',file=sm)
    print('111',file=sm)
    print('2222222',file=sm)
    print('333333333',file=sm)
    print('111',file=sm)
    print('2222222',file=sm)
    print('333333333',file=sm)
    print('111',file=sm)
    print('2222222',file=sm)
    print('333333333',file=sm)
    sm.flush()

    sys.exit(app.exec())



