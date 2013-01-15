#coding=utf-8
from django.http import HttpResponse

__author__ = 'Administrator'
import md5
import random
from pngcanvas import PNGCanvas

class ImageCode():
    text = None
    md5Text = None
    img = None
    width = 0
    height = 0
    #长度
    textX = 10
    textY = 10
    beginX = 5
    endX = 5
    beginY = 5
    endY = 5
    spare = 4

    def __init__(self,text=None):
        if(text==None):
            self.text = self.getRandom()
        else:
            self.text = text
            #self.getMd5Text()
        self.width = len(str(self.text))*(self.spare+self.textX)+self.beginX+self.endX
        self.height = self.textY + self.beginY + self.endY

    def create(self):
        self.img = PNGCanvas(self.width,self.height)
        self.img.color = [0xff,0xff,0xff,0xff]
        #self.img.color = [0x39,0x9e,0xff,0xff]
        #self.img.verticalGradient(1,1,self.width-2, self.height-2,[0xff,0,0,0xff],[0x60,0,0xff,0x80])
        self.img.verticalGradient(1,1,self.width-2, self.height-2,[0xff,0x45,0x45,0xff],[0xff,0xcb,0x44,0xff])

        for i in range(4):
            a = str(self.text)[i]
            self.writeText(a,i)

        return self.img.dump()

    def getRandom(self):
        intRand = random.randrange(1000,9999)
        return intRand

    def getMd5Text(self):
        m = md5.new()
        m.update(str(self.text))
        self.md5Text = m.hexdigest()

    def writeText(self,text,pos=0):
        if(text=="1"):
            self.writeLine(pos, "avc")
        elif(text=="2"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "hvtr")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "hvbl")
            self.writeLine(pos, "ahb")
        elif(text=="3"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "ahb")
            self.writeLine(pos, "avr")
        elif(text=="4"):
            self.writeLine(pos, "hvtl")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "avc")
        elif(text=="5"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "hvtl")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "hvbr")
            self.writeLine(pos, "ahb")
        elif(text=="6"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "avl")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "hvbr")
            self.writeLine(pos, "ahb")
        elif(text=="7"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "avr")
        elif(text=="8"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "avl")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "avr")
            self.writeLine(pos, "ahb")
        elif(text=="9"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "avr")
            self.writeLine(pos, "ahc")
            self.writeLine(pos, "ahb")
            self.writeLine(pos, "hvtl")
        elif(text=="0"):
            self.writeLine(pos, "aht")
            self.writeLine(pos, "avl")
            self.writeLine(pos, "avr")
            self.writeLine(pos, "ahb")

    '''
    type解释
    a:全部,部分上下
    h:一半
    h:横
    v:竖
    l:左，上
    c:中间
    r:右，下
    t:上
    b:下
    '''
    def writeLine(self,pos,type):
        if(type=="avl"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY
            )
        elif(type=="avc"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos+self.textX/2,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos+self.textX/2,
                self.beginY+self.textY
            )
        elif(type=="avr"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY
            )
        elif(type=="aht"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY,
            )
        elif(type=="ahc"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY/2,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY/2
            )
        elif(type=="ahb"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY
            )
        elif(type=="hvtl"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY/2
            )
        elif(type=="hvtr"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY/2
            )
        elif(type=="hvbl"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY/2,
                self.beginX+(self.textX+self.spare)*pos,
                self.beginY+self.textY
            )
        elif(type=="hvbr"):
            self.img.line(
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY/2,
                self.beginX+(self.textX+self.spare)*pos+self.textX,
                self.beginY+self.textY
            )

def display(request):
    img=ImageCode()
    img.create()
    imgcode=str(img.text)
    request.session['imgcode']=imgcode
    return HttpResponse(img.img.dump(),'image/png')