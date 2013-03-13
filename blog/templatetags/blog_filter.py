#coding=utf-8
__author__ = '王健'

from django import template
import re
register=template.Library()

@register.filter(name='keywordStyle')
def keywordStyle(count,stylelist):
    for i in range(0,len(stylelist)):
        if i==0 and count<=stylelist[i]:
            return i
        elif count>stylelist[i-1] and count<=stylelist[i]:
            return i
        else:
            return len(stylelist)-1


@register.filter(name='paperImageEffect')
def paperImageEffect(papercontent):
    contetn=papercontent
    imgtaglist=[]
    imgtagtupl=[]
    for img in re.findall('(?i)(<img.*?/>)',papercontent.replace('\n','').replace('\r','')):
        imgtaglist.append(img)
    for text in imgtaglist:
        for img in re.findall('(?i)src=[\'\"]{0,1}([^>\s\?&]*)[\'\"]{0,1}',text):
            imgtagtupl.append((text,'<a class="fancybox-effects-a" href="%s" data-fancybox-group="gallery" >%s</a>'%(img,text)))

    for text,imgtag in imgtagtupl:
        contetn=contetn.replace(text,imgtag)

    return contetn