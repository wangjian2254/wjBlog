#coding=utf-8
# Create your views here.
import logging
import os
import random
import urllib
import uuid
from django.contrib.sites.models import Site

from django.template.context import RequestContext

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
import ImageFile
import json
#def imageUp(request):
#    user=request.user
#    return render_to_response('default/adminedit.html',locals())
from django.views.decorators.csrf import csrf_exempt
from wjBlog.blog.models import WebSiteInfo
from wjBlog.ueditor.models import UeditorFile
from wjBlog.util.tool import domain_site
from wjBlog.settings import SITE_ID,UPLOAD_ROOT

fieldname='upfile'
imgtype=["gif" , "png" , "jpg" , "jpeg" , "bmp"]
filetype=["rar" , "zip" ]

errorInfo={'SUCCESS':'SUCCESS','NOFILE':u'未包含文件上传域','TYPE':u'不允许的文件格式','SIZE':u'文件大小超出限制','ENTYPE':u'请求类型ENTYPE错误','REQUEST':u'上传请求异常','IO':u'IO异常','DIR':u'目录创建失败','UNKNOWN':u'未知错误'}
maxSize=200000
filemaxSize=1100000
ue_separate_ue='ue_separate_ue'

def getResult():
    return {'original':'','url':'','title':'','state':''}

def isAllowFiles(filename,filetypes):
    type=filename.split('.')
    if type[-1].lower() in filetypes:
        return True
    else:
        return False
    return
def getSaveName(dir,filename):
    """
    判断是否存在文件名，如果存在，产生新的文件名
    """
    filename=str(uuid.uuid4())+'.'+filename.split('.')[1]
    while os.path.isfile(dir+filename):
        file_name=filename.split('.')
        filename=file_name[0]+str(random.randint(0,9))+'.'+file_name[1]
    return filename
def isAllowSize(size,maxsize):
    if size>maxsize:
        return False
    else:
        return True

@login_required
@csrf_exempt
@domain_site
def imageUp(funname,site,request):
    result=getResult()
    f=request.FILES[fieldname]
    if not isAllowFiles(f.name,imgtype):
        result['state']=errorInfo['TYPE']
    elif not isAllowSize(f.size,maxSize) :
        result['state']=errorInfo['SIZE']
    else:
        parser=ImageFile.Parser()
        for chunk in f.chunks():
            parser.feed(chunk)
        img=parser.close()
        newfilename=''
        ufile=UeditorFile()
        try:
            newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/',f.name)
            ufile.filename=f.name
            ufile.realfilename=newfilename
            ufile.size=f.size
            ufile.title=request.POST.get('pictitle','')
            ufile.type='image'
            ufile.site=WebSiteInfo.objects.get(pk=site.get('id'))
            ufile.user=request.user
            ufile.save()
            img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
        except Exception,e:
            ufile.delete()
            result['state']=errorInfo['DIR']

        else:
            result['state']=errorInfo['SUCCESS']
            result['title']=ufile.title
            result['url']=str(site.get('id'))+'/'+newfilename
    return HttpResponse(json.dumps(result))

@login_required
@csrf_exempt
@domain_site
def fileUp(funname,site,request):
    result=getResult()
    f=request.FILES[fieldname]
    if not isAllowFiles(f.name,filetype):
#        result['state']=errorInfo['TYPE']
        result['state']=u'只允许上传 rar 和 zip 格式的数据'
    elif not isAllowSize(f.size,filemaxSize) :
        result['state']=u'最大允许上传1Mb的文件'
    else:
        newfilename=''
        ufile=UeditorFile()
        try:
            newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/',f.name)
            ufile.filename=f.name
            ufile.realfilename=newfilename
            ufile.size=f.size
            ufile.title=request.POST.get('pictitle','')
            ufile.type='att'
            ufile.site=WebSiteInfo.objects.get(pk=site.get('id'))
            ufile.user=request.user
            ufile.save()
            fileatt=open(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename,'wb+')
            for chunk in f.chunks():
                fileatt.write(chunk)
            fileatt.close()

        except Exception,e:
            ufile.delete()
            result['state']=errorInfo['DIR']

        else:
            result['state']=errorInfo['SUCCESS']
            result['url']=str(site.get('id'))+'/'+newfilename
    return HttpResponse(json.dumps(result))




@csrf_exempt
@login_required
@domain_site
def getRemoteImage(funname,site,request):
    result={}
    url=request.POST.get("upfile")
    result['state']=u'远程图片抓取成功'
    arr=url.split(ue_separate_ue)
    outSrc=[]
    for i,uri in enumerate(arr):
        outSrc.append('')
        if not isAllowFiles(uri,imgtype):
            result['state']=errorInfo['TYPE']
            continue
        fileuri=urllib.urlopen(uri)
        if fileuri.getcode()==200 and fileuri.headers.type.find('image')!=-1:
            parser=ImageFile.Parser()
            for chunk in fileuri.readlines():
                parser.feed(chunk)
            fileuri.close()
            size=int(fileuri.headers.dict['content-length'])
            img=parser.close()
            newfilename=''
            ufile=UeditorFile()
            try:
                newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/',uri.split('/')[-1])
                ufile.filename=uri.split('/')[-1]
                ufile.realfilename=newfilename
                ufile.size=size
                ufile.title=''
                ufile.type='image'
                ufile.site=WebSiteInfo.objects.get(pk=site.get('id'))
                ufile.user=request.user
                ufile.save()
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            except Exception,e:
                ufile.delete()
                result['state']=errorInfo['DIR']
                continue
            else:
            #                result['state']=errorInfo['SUCCESS']
                outSrc.insert(i,str(site.get('id'))+'/'+newfilename)
            pass
        else:
            result['state']=u'图片地址错误'
            continue
    outstr=ue_separate_ue.join(outSrc)
    result2={}
    result2['url']=outstr
    result2['srcUrl']=url
    result2['tip']=result['state']
    return HttpResponse(json.dumps(result2))
@login_required
@csrf_exempt
@domain_site
def imageManager(funname,site,request):
    strs=''
#    uri='http://'+request.META['HTTP_HOST']+UPLOAD_URL
    uri=str(site.get('id'))+'/'
    for ufile in UeditorFile.objects.filter(site=WebSiteInfo.objects.get(pk=site.get('id'))):
        strs+=uri+ufile.realfilename+ue_separate_ue
    if strs:
        strs=strs[:0-len(ue_separate_ue)]
    return HttpResponse(strs)

@login_required
@csrf_exempt
@domain_site
def getMovie(funname,site,request):
    searchkey=request.POST.get('searchKey','').encode('utf-8')
    videotype=request.POST.get('videoType','')
    content=''
    try:
#        searchkey=urllib.quote(searchkey)
        url="http://api.tudou.com/v3/gw?method=item.search&appKey=myKey&format=json&"+ urllib.urlencode({'kw':searchkey})+"&pageNo=1&pageSize=20&channelId="+videotype+"&inDays=7&media=v&sort=s"
        videofile=urllib.urlopen(url)
        if 200==videofile.getcode():
            content+=videofile.read()
        videofile.close()
    except Exception,e:
        logging.error(str(e))
    return HttpResponse(content)
