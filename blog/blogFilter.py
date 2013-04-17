#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.shortcuts import render_to_response
HTTP_Str = 'http://'
HTTPS_Str = 'https://'
__author__ = u'王健'

def requestBlogContent(request):
    url=request.POST.get('blogurl','')
    if not url:
        return None
    import urllib2
    req=urllib2.urlopen(url)
    html=None
    try:
        html=req.read()
    except:
        return None
    if not html:
        return None
    return filterBlogContent(url,html)

def filterBlogContent(url,html):
    domain = ''
    if url.find(HTTP_Str) == 0:
        domain = url[len(HTTP_Str):]
    else:
        domain = url[len(HTTPS_Str):]
    domain = domain[:domain.find('/')]


def filterBlog_163(html):
    pass
def filterBlog_baidu(html):
    pass
def filterBlog_cnblogs(html):
    pass
def filterBlog_csdn(html):
    pass
def filterBlog_iteye(html):
    pass