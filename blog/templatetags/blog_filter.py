#coding=utf-8
__author__ = '王健'

from django import template
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