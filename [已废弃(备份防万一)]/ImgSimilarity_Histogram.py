

__all__=['ImgSimilarity_Histogram']

def ImgSimilarity_Histogram(npImg1,npImg2):
    size=(min(len(npImg1[0]),len(npImg2[0])),min(len(npImg1),len(npImg2)))
    return classify_hist_with_split(npImg1,npImg2,size)







#图片相似度(使用的是直方图算法)：https://blog.csdn.net/qq_38641985/article/details/118304624
#代码复制率90%+，不想探究算法，直接拿来用了

import cv2
import numpy as np


#通过得到RGB每个通道的直方图来计算相似度
def classify_hist_with_split(image1, image2, size=(256, 256)):
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data


# 计算单通道的直方图的相似值
def calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree





if __name__=="__main__":
    print("!")
    from time import sleep#休眠
    from PIL.ImageGrab import grab#用于获取屏幕截图

    sleep(5)
    print("!")
    im1=grab((0,0,1920,1080))
    img1=np.array(im1)

    sleep(5)
    print("!")
    im2=grab((0,0,1920,1080))
    img2=np.array(im2)

    im1.show()
    im2.show()

    n = ImgSimilarity_Histogram(img1, img2)
    
    print('三直方图算法相似度：', n)






