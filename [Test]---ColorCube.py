
#显示颜色立方
#花了老半天时间做出来的，结果没啥卵用...（就当练习了下np数组的一些基本操作吧

import sys
import cv2
import numpy as np

from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHBoxLayout,QWidget,QLabel,QVBoxLayout

from XJ_UsefulWidgets import XJ_NumInput#数字输入框
from XJ_UsefulWidgets import XJ_Slider_Horizon#水平滑动条
from XJ_UsefulWidgets import XJ_3DViewer,XJ_Cube,XJ_Point,XJ_Aspect




class XJ_LimitedValue(QWidget):#带有滑动条的数字输入框，仅此而已
    valueChanged=pyqtSignal(int)#槽信号，值发生变化时发送信号

    def __init__(self,parent=None,hint="数值："):
        super().__init__(parent)
        hbox=QHBoxLayout(self)

        label=QLabel(hint,self)
        num=XJ_NumInput(self)
        slider=XJ_Slider_Horizon(self)
        self.setFocusPolicy(Qt.ClickFocus)#让控件可以获取焦点
        
        num.valueChanged.connect(self.__NumChanged)
        slider.valueChanged.connect(self.__SliderChanged)
        hbox.addWidget(label)
        hbox.addWidget(num,1)
        hbox.addWidget(slider,5)

        self.__label=label
        self.__num=num
        self.__slider=slider
        self.__change=''#相当于一个锁，改值时避免发送两次信号。并且该值不为空时说明是哪个控件的数据是新的

    def SetSheet_Label(self,sheet):
        self.__label.setStyleSheet(sheet)
    def SetSheet_Num(self,sheet):
        self.__num.setStyleSheet(sheet)
    def SetSheet_Slider(self,sheet):
        self.__slider.setStyleSheet(sheet)

    def SetMinimum(self,value):
        self.__slider.setMinimum(value)
        self.__num.SetMinimum(value)
    def SetMaximum(self,value):
        self.__slider.setMaximum(value)
        self.__num.SetMaximum(value)
    def GetValue(self):
        if(self.__change=='N'):
            return self.__num.Get_Value()
        return self.__slider.value()
    def SetValue(self,value):
        self.__num.SetValue(value)

    def __NumChanged(self,value):
        if(self.__change!=''):
            self.__change='N'
            self.valueChanged.emit(value)
        self.__slider.setValue(value)
        self.__change=False
    def __SliderChanged(self,value):
        if(self.__change!=''):
            self.__change='S'
            self.valueChanged.emit(value)
        self.__num.SetValue(value)

        self.__change=False


def SetCube(cube,color):#对cube设置颜色图。color为三元元组，对应rgb
    r,g,b=(c+1 for c in color)

    axis_r=np.arange(0,r,1,np.uint8)#轴，把它们当刷子更容易理解
    axis_g=np.arange(0,g,1,np.uint8)
    axis_b=np.arange(0,b,1,np.uint8)

    #生成六面图片
    R,G=np.meshgrid(axis_r,axis_g)#np.meshgrid生成网格矩阵。np.flipud用于数组倒序
    B=np.zeros((g,r),np.uint8)
    Bottom=cv2.merge([B,G,R])#【底面】
    R,G=np.meshgrid(axis_r,np.flipud(axis_g))
    B=np.ones((g,r),np.uint8)*(b-1)
    Top=cv2.merge([B,G,R])#【顶面】

    R,B=np.meshgrid(axis_r,np.flipud(axis_b))
    G=np.zeros((b,r),np.uint8)
    Front=cv2.merge([B,G,R])#【正面】
    R,B=np.meshgrid(np.flipud(axis_r),np.flipud(axis_b))
    G=np.ones((b,r),np.uint8)*(g-1)
    Back=cv2.merge([B,G,R])#【背面】

    G,B=np.meshgrid(np.flipud(axis_g),np.flipud(axis_b))
    R=np.zeros((b,g),np.uint8)
    Left=cv2.merge([B,G,R])#【左面】
    G,B=np.meshgrid(axis_g,np.flipud(axis_b))
    R=np.ones((b,g),np.uint8)*(r-1)
    Right=cv2.merge([B,G,R])#【右面】

    cube.SetPict(XJ_Aspect.Front,Front)
    cube.SetPict(XJ_Aspect.Back,Back)
    cube.SetPict(XJ_Aspect.Bottom,Bottom)
    cube.SetPict(XJ_Aspect.Top,Top)
    cube.SetPict(XJ_Aspect.Left,Left)
    cube.SetPict(XJ_Aspect.Right,Right)

    cube.SetVectorX(XJ_Point(r,0,0))
    cube.SetVectorY(XJ_Point(0,g,0))
    cube.SetVectorZ(XJ_Point(0,0,b))

if __name__=='__main__':
    app = QApplication(sys.argv)
    color=[255,255,255]

    wid=QWidget()
    viewer=XJ_3DViewer(center=XJ_Point(128,128,128))#3D显示
    r=XJ_LimitedValue(wid,"红：")#用来控制颜色的
    g=XJ_LimitedValue(wid,"绿：")
    b=XJ_LimitedValue(wid,"蓝：")

    r.SetMaximum(255)
    g.SetMaximum(255)
    b.SetMaximum(255)
    r.SetValue(255)
    g.SetValue(255)
    b.SetValue(255)
    r.valueChanged.connect(lambda val:[exec("color[0]=val") , SetCube(cube,color) , viewer.UpdateCubes() , exec("viewer.camera.Camera_RotationCenter=XJ_Point(*(c>>1 for c in color))")])
    g.valueChanged.connect(lambda val:[exec("color[1]=val") , SetCube(cube,color) , viewer.UpdateCubes() , exec("viewer.camera.Camera_RotationCenter=XJ_Point(*(c>>1 for c in color))")])
    b.valueChanged.connect(lambda val:[exec("color[2]=val") , SetCube(cube,color) , viewer.UpdateCubes() , exec("viewer.camera.Camera_RotationCenter=XJ_Point(*(c>>1 for c in color))")])

    cube=XJ_Cube(XJ_Point(0,0,0),XJ_Point(256,256,256))
    SetCube(cube,color)
    viewer.AddCube(cube)


    vbox=QVBoxLayout(wid)
    vbox.addWidget(viewer,1)
    vbox.addWidget(r)
    vbox.addWidget(g)
    vbox.addWidget(b)

    wid.resize(1000,800)
    wid.show()
    viewer.camera.Camera_RotationCenter=XJ_Point(128,128,128)
    sys.exit(app.exec())



