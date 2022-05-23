# MC_AutoFishing

MC自动钓鱼，做这个小工具的动机很明显，就是不想钓鱼。</br>
鹦鹉壳有两个来源：钓鱼、打溺尸。其中溺尸拿鹦鹉壳实在太运气了(试过一个多个小时海上漂但愣是见不到拿壳的)，于是只能把目光锁定到钓鱼上面</br>
但钓鱼钓十来分钟我就厌了，宁可立马写个脚本出来使用也好过傻钓</br>
</br>

***

浮标下沉的判断逻辑我就弄的很简单了啊，就是判断特定颜色的像素个数，当浮标下沉时白色像素个数会显著减少，依此为判断依据


该项目中使用的部分关键函数/模块/类：</br>
PIL.ImageGrab.grab————抓取屏幕信息函数</br>
pymouse.PyMouse————鼠标模拟类(模拟右键点击)</br>
threading.Thread————线程类(其实应该用QThread的，但想着自己不熟QThread所以暂不冒风险对项目大改)</br>
time.sleep————休眠函数</br>
</br>



其实这个项目的核心部分不难(也就只是定时抓屏进行判断而已)，难的是UI界面编写，这实在是太困难了。</br>
如果说核心部分我花了一两天就弄好的话，UI可是做了我十天有多，把我人都做傻了(部分代码里存在不规范的地方，但懒得修了，没心思再去降耦)</br>
</br>
</br>
</br>

下载程序：<a href="https://github.com/Ls-Jan/MC_AutoFishing/releases/download/v1.0.0/XJ_MCAutoFishing.zip">MC_AutoFishing.zip</a></br>
不要问我为啥程序文件的压缩包那么大，那是python的问题，python打包出来的文件体积庞大已经是臭名昭著的了

# 运行演示

<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/0.gif"/>

</br>
</br>
</br>


# 说明

1、运行程序</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/1.png" width=50% height=50%/>

2、选定选区</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/2.png" width=50% height=50%/>

3、显示/隐藏选区</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/3.png" width=50% height=50%/>

4、点击“测试”</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/4.png" width=50% height=50%/>

5、开始自动钓鱼</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/5.png" width=50% height=50%/>

6、钓鱼出现问题时及时修改阈值</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/6.png" width=50% height=50%/>


# 备注
1、右侧的“像素颜色”和“颜色容差”一般不需要去设置，我已经调好的了，除非实在不好用的时候才去修改。更多的时候是修改那个阈值。</br>
2、如果指到数字时鼠标出现的手型的话那么该数字可以滚轮修改，也可以鼠标左键双击进行修改。</br>
<img src="https://github.com/Ls-Jan/MC_AutoFishing/blob/main/RunningDisplay%5BPNG%2CMP4%5D/1.png" width=50% height=50%/>
