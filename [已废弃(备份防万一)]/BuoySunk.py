
from PIL import Image

import cv2
import numpy as np
import matplotlib.pyplot as plt


__all__=['BuoySunk']

def BuoySunk(pilImg):#判断浮标是否下沉
    w=WhitePixelCount(pilImg)
    print(w)
    return w<100

def WhitePixelCount(pilImg,threshold=64):#计算图片内白色像素个数，threshold为阈值，仅3通道的值均大于该阈值时才判断它是不是白色
    img=cv2.cvtColor(np.array(pilImg), cv2.COLOR_RGBA2RGB)#转一下格式
    r,g,b=cv2.split(img)
    
    #因为不会用np，只能用各种看上去莫名其妙的方法来解决问题(估计有性能影响，总感觉有其他办法但一时找不到
    pos1=(abs(r-g)+abs(r-b)+abs(g-b)<48)#白色的三通道的值是相近的，所以相减的差值很小，以此作为白颜色的判断依据
    pos2=np.bitwise_and(r>threshold,g>threshold,b>threshold)#3通道的颜色均大于阈值threshold的才视为白色
    w=pos1[pos2]
    
    return w.sum()

if __name__=='__main__':
    BuoySunk(Image.open('1.png'))
    cv2.waitKey(0)


