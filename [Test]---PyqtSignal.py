#发现pyqt有一些地方存在跨线程的问题(子线程修改主线程的控件)，单独尝试解决


import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication,QTextEdit,QLabel

from PyQt5.QtCore import Qt,pyqtSignal,QObject


class Test(QObject):
    signal=pyqtSignal(str)
    def __init__(self,te):
        super().__init__()
        self.signal.connect(self.SetText)
        self.te=te
    def SetText(self,text):
        self.te.setText(text)

if __name__=='__main__':
    app = QApplication(sys.argv)
    
    te=QTextEdit()
    te.show()
        
#    Thread(target=lambda:te.append("AAA")).start()#简简单单就重现了问题
#    Thread(target=lambda:te.setText("AAA")).start()#这个更严重，直接翻车

#    lb=QLabel()
#    lb.show()
#    Thread(target=lambda:lb.setText("AAA")).start()#不清楚问题原因。因为这个没有报错

    test=Test(te)
    Thread(target=lambda:test.signal.emit("1000")).start()#通过信号量的方式可以规避这个问题。
    #主流意见一般是：子线程别随便改UI(高概率翻车)，要改就通过pyqt的线程(QThread)来处理，或者使用信号量(pyqtSignal)
    #QThread暂时不想接触，先摸了

    
    sys.exit(app.exec())
    
    
    




    
    