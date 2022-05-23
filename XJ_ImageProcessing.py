

import cv2
import numpy as np
from PIL import Image


__all__=['PixelCount']

def PixelCount(pilImg,color=(224,224,224),threshold=10):#判断颜色与color相近的像素个数。threshold为阈值
    img=cv2.cvtColor(np.array(pilImg), cv2.COLOR_RGBA2RGB)#转一下格式
    r,g,b=cv2.split(img)

    pos1=np.bitwise_and(r>=color[0]-threshold,g>=color[1]-threshold,b>=color[2]-threshold)
    pos2=np.bitwise_and(r<=color[0]+threshold,g<=color[1]+threshold,b<=color[2]+threshold)
    pos=np.bitwise_and(pos1,pos2)
    return pos.sum()
    


if __name__=='__main__':
    print(PixelCount(Image.fromarray(np.array(np.random.rand(100,200,3)*255,np.uint8))))
    cv2.waitKey(0)


