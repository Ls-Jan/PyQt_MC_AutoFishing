#看看lambda好不好用
#结论：还行，没翻车，还是能用的


class Test:
    def __init__(self,num):
        self.num=num
        self.func=lambda:print(self.num)#看来在类里面设置lambda函数不会翻车呢，挺好的挺好的，变量域真是不错

print()
lst=[Test(i) for i in range(10)]
for t in lst:
    t.func()






    
print()
lst=[lambda :print(i) for i in range(10)]#这里翻车hin(很)正常，这完完全全就是变量域的问题
for func in lst:
    func()






print()
lst=[(lambda i:lambda :print(i))(i) for i in range(10)]#想不像上面那样翻车就搞闭包(闭包的主要目的是创建个变量域)
for func in lst:
    func()
