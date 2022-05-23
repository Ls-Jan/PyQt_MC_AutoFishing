
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QVBoxLayout,QLabel
from PyQt5.QtCore import Qt,pyqtSignal

from XJ_UsefulWidgets import XJ_NumInput

__all__=['XJ_NumInput_Exp']

class XJ_NumInput_Exp(QLabel):#指数表示的数(有效数字为3位)，说白了就是两个XJ_NumInput瞎组合在一起的老土玩意儿。显示效果为[系数]×10^[指数]
    #继承QLabel而不是QWidget原因是QWidget没法搞样式表
    valueChanged=pyqtSignal()#槽信号，值修改时发送信号。至于为什么不发送int呢，因为valueChanged.emit(int)发送的数的大小会被限制(过大的数会造成溢出，就离谱)，我也不清楚，反正很离谱就是了
    def __init__(self,parent=None):
        super().__init__(parent)

        self.__factor=XJ_NumInput(self)#系数
        self.__exp=XJ_NumInput(self)#指数
        self.__lb=QLabel('×',self)
        self.__InitUI()
        self.__InitConfig()

    def __InitUI(self):#设置UI
        hbox=QHBoxLayout(self)
        hbox.addWidget(self.__factor)
        hbox.addWidget(self.__lb)
        hbox.addWidget(self.__exp)
        hbox.setContentsMargins(2,2,2,2)

        self.setStyleSheet(#不会用CSS，都是乱写的，麻了
        '''
            *{
                background-color:#F0F0F0 ;
                border:1px solid #00AAFF ;
            }
            .QLabel{
                border:none ;
            }
            .XJ_NumInput{
                border:none
            }
        ''')

    def __InitConfig(self):#设置其他东西
        factor=self.__factor
        exp=self.__exp

        factor.SetTextFormat(lambda num:'<font color=#0088FF>{}</font>'.format(num))#系数
        exp.SetTextFormat(lambda num:'10<sup><font color=#0088FF>{}</font><sup>'.format(num))#指数样式
        factor.SetAlignment(Qt.AlignRight)
        exp.SetAlignment(Qt.AlignLeft)
        factor.SetValueRange(0,999)
        exp.SetValueRange(0,1000)

        factor.valueChanged.connect(lambda val:self.valueChanged.emit())
        exp.valueChanged.connect(lambda val:self.valueChanged.emit())

        self.setFixedHeight(38)
        self.setMinimumWidth(100)
        self.__lb.setFixedHeight(20)
        self.setFocusPolicy(Qt.ClickFocus|Qt.WheelFocus)#让控件可以获取焦点

    def GetValue(self):
        factor=self.__factor.GetValue()
        exp=self.__exp.GetValue()
        return factor*pow(10,exp)

    def SetValue(self,val):
        factor=int(val)
        exp=0
        minVal,maxVal=self.__factor.GetValueRange()
        while(factor%10==0 or minVal>factor or maxVal<factor):
            factor=int(factor/10)
            exp=exp+1
        self.__factor.SetValue(factor)
        self.__exp.SetValue(exp)
    def SetValueRange_Factor(self,minVal,maxVal):
        self.__factor.SetValueRange(minVal,maxVal)
    def SetValueRange_Exp(self,minVal,maxVal):
        self.__exp.SetValueRange(minVal,maxVal)

if __name__=='__main__':
    app = QApplication(sys.argv)
    exp1=XJ_NumInput_Exp()
    exp2=XJ_NumInput_Exp()

    wid=QWidget()
    box=QVBoxLayout(wid)
    box.addWidget(exp1)
    box.addWidget(exp2)
    wid.show()

    exp1.valueChanged.connect(lambda :print("exp1：",exp1.GetValue()))
    exp2.valueChanged.connect(lambda :print("exp2：",exp2.GetValue()))
    exp1.SetValue(200)
    exp2.SetValueRange_Factor(10,100)
    exp2.SetValue(12345)
    exp2.SetValueRange_Exp(-100,100)

    sys.exit(app.exec())

















