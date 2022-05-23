
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QVBoxLayout,QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from XJ_BaseScreenMonitor import XJ_BaseScreenMonitor#基础监控器
from XJ_UsefulWidgets import XJ_ColorChoose#颜色选择
from XJ_UsefulWidgets import XJ_NumInput#数字输入
from XJ_NumInput_Exp import XJ_NumInput_Exp#指数型数字(3位有效数)输入
from XJ_ImageProcessing import PixelCount#判断pilImg中颜色与color相近的像素个数：PixelCount(pilImg,color=(224,224,224),threshold=10)

from pymouse import PyMouse#用于模拟鼠标行为(鼠标右键)
from time import sleep#用于休眠

class XJ_MCAutoFishing(QWidget):#MC自动钓鱼
    def __init__(self,parent=None):
        super().__init__(parent)

        self.__monitor=XJ_BaseScreenMonitor(self)#大头
        self.__color=XJ_ColorChoose(self)#颜色选择
        self.__colorTolerance=XJ_NumInput(self)#颜色容差
        self.__threshold=XJ_NumInput_Exp(self)#阈值
        self.__mouse=PyMouse()#鼠标实例

        self.__InitUI()
        self.__InitConfig()

    def __InitUI(self):#设置UI界面
        color=self.__color
        colorToler=self.__colorTolerance
        threshold=self.__threshold
        monitor=self.__monitor

        wids=QLabel()
        wids.setLayout(QVBoxLayout())
        widsLst=[#老懒狗了
            (color,QLabel('    像素颜色：')),
            (colorToler,QLabel('    颜色容差：')),
            (threshold,QLabel('像素个数阈值：'))]
        for item in widsLst:
            wid=QWidget(self)
            hbox=QHBoxLayout(wid)
            hbox.addStretch(2)
            hbox.addWidget(item[1])
            hbox.addWidget(item[0],3)
            wids.layout().addWidget(wid)
        wids.layout().addStretch(1)
        wids.layout().setContentsMargins(0,0,0,0)
        
        hbox=QHBoxLayout(self)
        vbox=QVBoxLayout()
        vbox.addWidget(wids)
        vbox.addStretch(1)
        hbox.addWidget(monitor,10)
        hbox.addStretch(1)
        hbox.addLayout(vbox,5)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)#窗口置顶
        self.setWindowTitle("MC自动钓鱼")#设置窗口标题
        self.setWindowIcon(QIcon('icon.png'))#设置图标
        self.setFocusPolicy(Qt.ClickFocus|Qt.WheelFocus)#让控件可以获取焦点
        self.setMinimumWidth(900)
        self.setMinimumHeight(200)
        self.setWindowOpacity(0.85)#窗口透明
        monitor.setMinimumWidth(500)
        wids.setMinimumWidth(300)
        wids.setMinimumHeight(180)

        #设置样式表
        self.setStyleSheet(#设置所有组件背景为黑色
        '''
            background-color:#080808 ;
        ''')
        colorToler.setStyleSheet(#颜色灵敏度的字体设置为白色
        '''
            color:#FFFFFF
        ''')
        wids.setStyleSheet(#给右侧组件设置一下边框
        '''
            #wids{
                border:2px solid rgb(0,192,255) ;
            }
        ''')
        for item in widsLst:
            item[1].setStyleSheet(#给那些label设置一下字体颜色
            '''
                color:#FFFFFF ;
                font-size:16px ;
            ''')
            item[1].setAlignment(Qt.AlignVCenter)
        threshold.setStyleSheet(#不会用CSS，都是乱写的.，而且在这里写感觉也很不规范
        '''
            *{
                background-color:#080808 ;
                border:1px solid #00AAFF ;
            }
            .QLabel{
                border:none ;
                color:#FFFFFF ;
            }
            .XJ_NumInput{
                border:none ;
                color:#FFFFFF ;
            }
        ''')
        wids.setObjectName('wids')

        #设置monitor的一些组件(主要是去设置按钮的文本
        widgets=monitor.GetWidgets()
        widgets['btn_run'].setText(' 开钓！')

        monitor.SetOutputPrompt('<font size=2 color=#00FFFF>></font>')#设置文本框行首提示符
        monitor.SetOuputContextTag('<font size=2 color=#FFFF00>{}</font>')#设置文本框的输出文本的样式
        monitor.UseDefaultLayout()#使用预置好的布局
        monitor.UseDefaultStyleSheet()#使用预置好的样式表
        monitor.clear()#清空文本框


    def __InitConfig(self):#额外设置
        color=self.__color
        colorToler=self.__colorTolerance
        threshold=self.__threshold
        monitor=self.__monitor

        colorToler.SetValueRange(0,255)#设置颜色容差取值范围
        colorToler.SetValue(50)#设置颜色容差
        threshold.SetValue(80)#设置阈值
        color.SetColor((182,182,182))#设置颜色
        threshold.SetValueRange_Factor(1,999)
        threshold.SetValueRange_Exp(0,3)

        monitor.SetFunc_Test(self.__Func_Test)#设置回调函数
        monitor.SetFunc_Run(self.__Func_Run)#设置回调函数

    def __Func_Test(self,pilImg):
        monitor=self.__monitor
        rst=PixelCount(pilImg,self.__color.GetColor(),self.__colorTolerance.GetValue())

        threshold=self.__threshold.GetValue()
        printText='【{}】个像素，'+('超出【{}】' if rst>threshold else '在【{}】以内')
        print(printText.format(rst,threshold),file=monitor,flush=True)

    def __Func_Run(self,pilImg):
        monitor=self.__monitor
        rst=PixelCount(pilImg,self.__color.GetColor(),self.__colorTolerance.GetValue())
        threshold=self.__threshold.GetValue()

        print('浮标浮动中...({:<4})'.format(rst),file=monitor,flush=True)
        if(rst<=threshold):
            mouse=self.__mouse
            mouse.click(*mouse.position(),2,1)#点击右键一次
            print('<font color=#FF0000 size=3>【浮标消失，收竿】</font>',file=monitor,flush=True)
            sleep(0.5)
            mouse.click(*mouse.position(),2,1)#点击右键一次
            print('<font color=#FF0000 size=3>【抛竿】</font>',file=monitor,flush=True)
            sleep(3)


if __name__=='__main__':
    app = QApplication(sys.argv)

    autoFishing=XJ_MCAutoFishing()
    autoFishing.show()

    sys.exit(app.exec())

















