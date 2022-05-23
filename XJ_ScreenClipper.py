

import sys
from PyQt5.QtGui import QPainter,QPen,QColor
from PyQt5.QtCore import Qt,QRect,QPoint,pyqtSignal
from PyQt5.QtWidgets import QApplication,QWidget




class XJ_ScreenClipper(QWidget):#屏幕选区器
    clipChanged=pyqtSignal()#当选区发生变化时触发
    dragFinished=pyqtSignal()#左键抬起(结束拖拽)时触发
    clipVisibleChanged=pyqtSignal()#当选区出现/消失时触发
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__borderWidth=2#边界粗细
        self.__borderMargin=4#边界的探测宽度(用于鼠标对边界的检测
        self.__borderColor=QColor(255,0,0)#边界颜色
        self.__clipColor=QColor(0,0,0,48)#选区颜色
        self.__pos=None#鼠标位置
        self.__clipChanged=False#用于判断当前是不是拖拽选区中
        self.__clip=None#选取的区域
        self.__anchor=None#离鼠标最近的边界
        self.__showClip=True#显示选区(主要用于实现选区的移动操作)。当该值为False时仅显示选区边框

        self.setMouseTracking(True)#时刻捕捉鼠标移动
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.ToolTip)#窗口置顶+窗体无边界+去除任务栏图标(ToolTip属实好用)
        self.setAttribute(Qt.WA_TranslucentBackground,True)#透明背景。该属性要和Qt.FramelessWindowHint配合使用，单独用的话不生效
#        self.setAttribute(Qt.WA_TransparentForMouseEvents,True)#点击穿透。在这里这个功能不生效
#        self.setWindowOpacity(0.4)#这个属实不好用，把所有控件全透明化了。这仅适用于脱离焦点变透明的情况，例如这个：https://lanzao.blog.csdn.net/article/details/89495395
        self.MaximumArea()

    def MaximumArea(self):#将选取范围最大化，一般不需要调用。不设置为私有仅仅以防万一
        #多屏的分辨率信息：https://blog.csdn.net/ieeso/article/details/93717182
        self.ClearClip()
        desktop = QApplication.desktop()
        L,T,R,B=0,0,0,0
        for i in range(desktop.screenCount()):
            rect=desktop.screenGeometry(i)
            rL,rT,rR,rB=self.__GetLTRB(rect)
            if(L>rL):
                L=rL
            if(R<rR):
                R=rR
            if(T>rT):
                T=rT
            if(B<rB):
                B=rB
        self.setGeometry(L,T,R-L+1,B-T+1)

    def GetClip(self):#返回选区信息(QRect)
        if(self.__clip):
            L,T=self.pos().x(),self.pos().y()
            rst=QRect(self.__clip)
            rst.moveLeft(L+rst.left())
            rst.moveTop(T+rst.top())
            return rst
        else:
            return QRect(0,0,0,0)

    def ClearClip(self):#清除选区
        if(self.__clip):
            self.clipChanged.emit()
        self.__clip=None
        self.update()
    
    def SetBorderColor(self,color:QColor):#设置边界颜色
        self.__borderColor=color
        self.update()
    def SetClipColor(self,color:QColor):#设置选区颜色
        self.__clipColor=color
        self.update()
    def SetBorderWidth(self,width:int):#设置边界粗细
        self.__borderWidth=width
        self.update()
    def SetClipVisible(self,flag:bool):#设置选区可见(选区边界始终可见)
        self.__showClip=flag
        self.update()


    def paintEvent(self,event):
        painter=QPainter(self)
        if(self.__clip):
            if(self.__showClip):
                painter.fillRect(self.__clip,self.__clipColor)
            painter.setPen(QPen(QColor(0,255,0,1),(self.__borderWidth+self.__borderMargin)<<1))
            painter.drawRect(self.__clip)
            painter.setPen(QPen(self.__borderColor,self.__borderWidth))
            painter.drawRect(self.__clip)
        else:
            area=self.geometry()
            area.moveTopLeft(QPoint(0,0))
            painter.fillRect(area,QColor(0,0,0,48))

    def hideEvent(self,event):
        if(self.__clip):
            self.__clip=None
            self.clipVisibleChanged.emit()
            self.clipChanged.emit()
            self.show()
            self.update()
            self.hide()
        
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:#按下左键
            self.__pos=event.pos()
        elif event.button()==Qt.RightButton:#按下右键
            if(self.__clip):
                self.__showClip=False
                self.update()
    
    def mouseDoubleClickEvent(self,event):
        if event.button()==Qt.RightButton:#双击右键，切换选区的可见
            self.__showClip=not self.__showClip
            self.update()
            
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.LeftButton:#抬起左键
            if(self.__clipChanged):
                self.dragFinished.emit()
                self.__clipChanged=False
        
    def mouseMoveEvent(self,event):
        pos=event.pos()
        anchor=self.__anchor

        if(event.buttons() & Qt.LeftButton):#左键拖拽
            self.__clipChanged=True
            if(self.__clip==None):
                self.__clip=QRect(pos.x(),pos.y(),1,1)
                self.__anchor='RB'
                self.__pos=pos
                self.clipVisibleChanged.emit()
            else:
                dx=pos.x()-self.__pos.x()
                dy=pos.y()-self.__pos.y()
                L,T,R,B=self.__GetLTRB(self.__clip)
                if(len(anchor)==0):
                    anchor='LTRB'
                if(anchor.find('L')!=-1):#移动左边界
                    L=L+dx
                if(anchor.find('R')!=-1):#移动右边界
                    R=R+dx
                if(anchor.find('T')!=-1):#移动上边界
                    T=T+dy
                if(anchor.find('B')!=-1):#移动下边界
                    B=B+dy
                if(L>R):
                    L,R=R,L
                if(T>B):
                    T,B=B,T
                    
                self.__clip=QRect(L,T,R-L+1,B-T+1)
                self.__pos=pos
            self.clipChanged.emit()
        self.__anchor=self.__GetNearestBorder(pos)
        self.__SetCursor()
        self.update()

    def __GetNearestBorder(self,pos):#判断距离最近的边，返回结果有8种(均为字串)，对应四边和四角：L、T、R、B、LT、LB、RT、RB。如果返回空串就当作距离太远吧
        rst=''

        clip=self.__clip
        if(clip):
            L=clip.left()
            T=clip.top()
            R=clip.right()
            B=clip.bottom()

            x=pos.x()
            y=pos.y()

            DL=abs(L-x)
            DR=abs(R-x)
            DT=abs(T-y)
            DB=abs(B-y)

            m=self.__borderWidth+self.__borderMargin+1

            if(DL<m or DR<m):
                rst=rst+('L' if DL<DR else 'R')
            if(DT<m or DB<m):
                rst=rst+('T' if DT<DB else 'B')
        return rst

    def __SetCursor(self):#根据self.__anchor设置光标
        anchor=self.__anchor
        if(len(anchor)>1):
            if(anchor=='LT' or anchor=='RB'):
                self.setCursor(Qt.SizeFDiagCursor)#左上右下
            else:
                self.setCursor(Qt.SizeBDiagCursor)#右上左下
        elif(len(anchor)>0):
            if(anchor=='L' or anchor=='R'):
                self.setCursor(Qt.SizeHorCursor)#左右
            else:
                self.setCursor(Qt.SizeVerCursor)#上下
        else:
            self.setCursor(Qt.SizeAllCursor)

    def __GetLTRB(self,rect:QRect):#太烦了，索性这么做。返回rect的左上右下的值
        return rect.left(),rect.top(),rect.right(),rect.bottom()
        
        




if __name__=='__main__':
    app = QApplication(sys.argv)

    sc= XJ_ScreenClipper()
    sc.show()

    sc.SetClipColor(QColor(64,0,0,192))
    sc.SetBorderColor(QColor(0,255,0))
    sc.SetBorderWidth(5)
#    sc.SetClipVisible(False)
#    sc.clipChanged.connect(lambda:print(sc.GetClip()))

    sys.exit(app.exec())











