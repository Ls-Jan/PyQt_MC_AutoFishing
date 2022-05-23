

import sys
from PyQt5.QtGui import QPainter,QPen,QColor,QBrush
from PyQt5.QtCore import Qt,QRect,QPoint
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QLabel


class XJ_TransparentBox(QWidget):#透明窗口
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__width=2#边界粗细
        self.__margin=6#边界的额外宽度(用于鼠标对边界的检测
        self.__borderColor=QColor(255,0,0)#边界颜色
        self.__rect=None#边界(QRect的格式为“左上宽高”
        self.__pos=None#鼠标的位置
        self.__anchor=None#离鼠标最近的边界
        
        self.setMouseTracking(True)#时刻捕捉鼠标移动
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.ToolTip)#窗口置顶+窗体无边界+去除任务栏图标(ToolTip属实好用)
#        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.ToolTip)#窗口置顶+窗体无边界+去除任务栏图标(ToolTip属实好用)
        self.setAttribute(Qt.WA_TranslucentBackground,True)#该属性要和Qt.FramelessWindowHint配合使用，单独用的话不生效
        self.setAttribute(Qt.WA_TransparentForMouseEvents,True)#点击穿透
#        self.setWindowOpacity(0.4)#这个属实不好用，把所有控件全透明化了。这仅适用于脱离焦点变透明的情况，例如这个：https://lanzao.blog.csdn.net/article/details/89495395
        self.resize(800,500)
        

    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:#按下左键
            self.__pos=event.globalPos()
            
            
    def mouseMoveEvent(self,event):
        pos=event.globalPos()
        anchor=self.__anchor
        
        if(event.buttons() & Qt.LeftButton):#左键拖拽
            rect=self.geometry()
            dx=pos.x()-self.__pos.x()
            dy=pos.y()-self.__pos.y()
            L=rect.left()
            T=rect.top()
            R=rect.right()
            B=rect.bottom()
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
                if(anchor.find('L')!=-1):
                    anchor=anchor.replace('L','R')
                else:
                    anchor=anchor.replace('R','L')
            if(T>B):
                T,B=B,T
                if(anchor.find('T')!=-1):
                    anchor=anchor.replace('T','B')
                else:
                    anchor=anchor.replace('B','T')
            if(len(anchor)<=2):
                self.__anchor=anchor
                self.__SetCursor()
            rect=QRect(L,T,R-L+1,B-T+1)
            if(rect.isValid() and abs(rect.width())>self.__width and abs(rect.height())>self.__width):
                QApplication.processEvents()
                self.move(rect.left(),rect.top())
                self.resize(rect.width(),rect.height())
#                self.setGeometry(rect)
                QApplication.processEvents()
                self.__pos=pos
        else:#设置光标
            self.__anchor=self.__GetNearestBorder(event.pos())
            self.__SetCursor()
            
        
        



        
        
    def resizeEvent(self,event):#设置self.__rect
        m=self.__margin
        w=self.size().width()
        h=self.size().height()

        L=m
        T=m
        R=w-m
        B=h-m
        self.__rect=QRect(L,T,R-L+1,B-T+1)

    def paintEvent(self,event):#绘制边界
        painter=QPainter(self)
        painter.setPen(QPen(QColor(0,255,0,1),self.__margin<<1))
        painter.drawRect(self.__rect)
        painter.setPen(QPen(self.__borderColor,self.__width))
        painter.drawRect(self.__rect)


    def __GetNearestBorder(self,pos):#判断距离最近的边/点，返回结果有8种(均为字串)，对应四边和四角：L、T、R、B、LT、LB、RT、RB。如果返回空串就当作距离太远吧
        rect=self.__rect

        L=rect.left()
        T=rect.top()
        R=rect.right()
        B=rect.bottom()

        x=pos.x()
        y=pos.y()

        DL=abs(L-x)
        DR=abs(R-x)
        DT=abs(T-y)
        DB=abs(B-y)

        m=self.__margin+self.__width

        rst=''
        if(DL<m or DR<m):
            rst=rst+('L' if DL<DR else 'R')
        if(DT<m or DB<m):
            rst=rst+('T' if DT<DB else 'B')
        return rst



    def __SetCursor(self):#设置光标
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








if __name__=='__main__':
    app = QApplication(sys.argv)

    tb= XJ_TransparentBox()
    tb.show()

    sys.exit(app.exec())

















