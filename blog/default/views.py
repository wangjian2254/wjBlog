#coding=utf-8
# Create your views here.
import logging
import traceback
import uuid
import ImageFile
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.html import strip_tags
from wjBlog.blog.default.defaultsettings import INDEX_LEFT_SUBNUM,ALBUM_LIST_LIMIT,SWFUPLOAD_TITLE_TYPE,INDEX_LEFT_KEYWORD,PAPERIMAGE_SIZE_WIDTH_BIG, PAPERIMAGE_SIZE_WIDTH_MID, PAPERIMAGE_SIZE_WIDTH_SMALL, PAPERIMAGE_SIZE_HEIGH_SMALL
from wjBlog.blog.form import EmailSubscribe
from wjBlog.blog.models import WebSiteInfo, Paper, Keyword, Guest, PaperImage, SubscribeMail
from wjBlog.ueditor.models import UeditorFile
from wjBlog.ueditor.views import isAllowFiles, isAllowSize, getSaveName
from wjBlog.util.tool import completePage
from wjBlog.blog.default.defaultsettings import TITLE_COMMENT_LIST,INDEX_LEFT_ADMININFO,INDEX_LEFT_COMMENT,PAPER_INDEX_KEY,INDEX_LEFT_MENULIST,INDEX_LEFT_SHOWNUM,MENU_ALL_LIST,PAPER_LIST_LIMIT
from django.core.cache import cache
from wjBlog.blog.models import Title, Replay, Menu, WebSiteDomain
from wjBlog.settings import CACHE_TIMEOUT,UPLOAD_ROOT,UPLOAD_URL
import json
def left(site,viewmap):
    leftmap={}
    ############# 最近留言
    commentlist=cache.get(INDEX_LEFT_COMMENT+str(site.get('id')))
    if not commentlist:
        commentlist=[]
        replayquery=Replay.objects.filter(site=site.get('id')).filter(isPub=True).order_by('-createDate')[:10]
        for replay in replayquery:
#            replay.url=replay.paperUrl()
            commentlist.append(replay)
        cache.set(INDEX_LEFT_COMMENT+str(site.get('id')),commentlist,CACHE_TIMEOUT)
    leftmap['commentlist']=commentlist

    ############# 关键字
    keywordmap=cache.get(INDEX_LEFT_KEYWORD+str(site.get('id')))
    if not keywordmap:
        keywordlist=[]
        keywordstyle=[]
        keywordquery=Keyword.objects.filter(site=site.get('id')).order_by('id')
        for keyword in keywordquery:
            keyword.count=Title.objects.filter(site=site.get('id')).filter(keywords=keyword).count()
            keywordlist.append(keyword)
            keywordstyle.append(keyword.count)
        keywordstyle.sort()
        if len(keywordstyle)>20:
            size=len(keywordstyle)/10
            keywordsj=[]
            for i in range(0,10):
                keywordsj.append(keywordstyle[i*size])
        else:
            keywordsj=keywordstyle[-10:]
        keywordmap={'keywordlist':keywordlist,'keywordstyle':keywordsj}
        cache.set(INDEX_LEFT_KEYWORD+str(site.get('id')),keywordmap,CACHE_TIMEOUT)
    leftmap['keywordlist']=keywordmap.get('keywordlist',[])
    leftmap['keywordstyle']=keywordmap.get('keywordstyle',[])

    ############ 栏目最新文章
    menulist=cache.get(INDEX_LEFT_MENULIST+str(site.get('id')))
    if not menulist:
        menulist=[]
        menuquery=Menu.objects.filter(site=site.get('id')).filter(type='paper').filter(link=None).order_by('index')
        for menu in menuquery:
            if 0<Title.objects.filter(menu=menu).count():
                paperlist=[]
                paperquery=Title.objects.filter(menu=menu).filter(isPub=True).order_by('-releaseDate')[:5]
                for paper in paperquery:
                    paperlist.append(paper)
                menu.paperlist=paperlist
                menulist.append(menu)

        cache.set(INDEX_LEFT_MENULIST+str(site.get('id')),menulist,CACHE_TIMEOUT)
    leftmap['menulist']=menulist
    ################# 访问统计
    showNum=cache.get(INDEX_LEFT_SHOWNUM+str(site.get('id')))
    if not showNum:
        website=WebSiteDomain.objects.get(pk=site.get('webdomainid'))
        showNum=website.showNum
        cache.set(INDEX_LEFT_SHOWNUM,showNum,300)
    leftmap['showNum']=showNum

    ##################个人简介
    adminInfo=cache.get(INDEX_LEFT_ADMININFO+str(site.get('id')))
    if not adminInfo:
        websiteinfo=WebSiteInfo.objects.get(pk=site.get('id'))
        adminInfo={'img':websiteinfo.author.img,'content':websiteinfo.author.desc}
        cache.set(INDEX_LEFT_ADMININFO+str(site.get('id')),adminInfo,CACHE_TIMEOUT)
    leftmap['adminInfo']=adminInfo

    ################### 电子订阅数量
    subscribeNum=cache.get(INDEX_LEFT_SUBNUM+str(site.get('id')))
    if  None==subscribeNum:
        subscribeNum=SubscribeMail.objects.filter(site=site.get('id')).count()
        cache.set(INDEX_LEFT_SUBNUM+str(site.get('id')),subscribeNum,CACHE_TIMEOUT)
    leftmap['subscribeNum']=subscribeNum
    viewmap['left']=leftmap
    return

def menu(site,viewmap):
    menulist=cache.get(MENU_ALL_LIST+str(site.get('id')))
    if not menulist:
        menulist=[]
        for menu in Menu.objects.filter(site=site.get('id')).filter(type='paper').filter(link=None).order_by('index'):
            menulist.append(menu)
        cache.set(MENU_ALL_LIST+str(site.get('id')),menulist,CACHE_TIMEOUT)
    viewmap['menulist']=menulist


def commentlist(site,viewmap,titleid,paperid):
    replaylist=cache.get(TITLE_COMMENT_LIST+str(site.get('id'))+str(titleid)+'p'+str(paperid))
    if not replaylist:
        replayquery=Replay.objects.filter(site=site.get('id')).filter(title=titleid).filter(paperid=paperid).filter(isPub=True).order_by('createDate')
        replaylist=[]
        for replay in replayquery:
            rmap={}
            rmap['id']=replay.id
            rmap['titleid']=replay.title_id
            rmap['face']=replay.face
            rmap['content']=replay.content
            rmap['paperid']=replay.paperid
            rmap['createDate']=replay.createDate.strftime('%Y年%m月%d日 %H:%M:%S')
            rmap['fatherid']=replay.fatherid_id
            rmap['isAdmin']=replay.isAdmin
            if replay.guest:
                rmap['guest']=replay.guest.nickname
            if replay.admin:
                rmap['admin']=replay.admin.get_full_name()
            replaylist.append(rmap)
    viewmap['commentlist']=replaylist

def index(site,request):
    '''
    index 模板页 方法
    '''
    viewmap={}
    paperlist=cache.get(PAPER_INDEX_KEY+str(site.get('id')))
    if not paperlist:
        paperlist=[]
        for paper in Title.objects.filter(site=site.get('id')).filter(isPub=True).order_by('-releaseDate')[:10]:
            paper.replyNum=Replay.objects.filter(title=paper).count()
            if paper.type in ['image','album']:
                firstImageList=PaperImage.objects.filter(title=paper).order_by('index')[:3]
                paper.imglist=[]
                for img in firstImageList:
                    paper.imglist.append({'imgsmall':img.getImgUrlsmall(site.get('id')),'imgbig':img.getImgUrlmid(site.get('id'))})
#                    paper.imglist=firstImageList[0]
#                    paper.imglist.imgsmal=album.firstImage.getImgUrlsmall(site.get('id'))
            paperlist.append(paper)
        cache.set(PAPER_INDEX_KEY+str(site.get('id')),paperlist,CACHE_TIMEOUT)
    viewmap['paperlist']=paperlist
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def blogAdmin(site,request):
    '''
    blog 管理界面
    '''
    viewmap={}


    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def manageMenu(site,request):
    viewmap={}
#    menulist=[]
#
#    for menuitem in Menu.objects.filter(site=site.get('id')).filter(link=None).order_by('index'):
#        menulist.append(menuitem)
#    viewmap['menulist']=menulist

    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def manageMenu_save(site,request):
    if 'POST'!=request.method.upper():
        return HttpResponseRedirect('/blog/Admin/manageMenu')
    msg=u'操作成功'
    viewmap={}
    id=request.POST.get('id','')
    indexnum=request.POST.get('index',0)
    if id:
        menuitem=Menu.objects.get(pk=id)
    else:
        menuitem=Menu()
        menuitem.site=WebSiteInfo.objects.get(pk=site.get('id'))
        lastmenuquery=Menu.objects.filter(site=site.get('id')).filter(type='paper').filter(link=None).order_by('-index')[:1]
        if 0==len(lastmenuquery):
            menuitem.index=1
        else:
            menuitem.index=lastmenuquery[0].index+1
    if not menuitem:
        msg=u'操作错误'
    else:
        try:
            indexnum=int(indexnum)

        except :
            msg=u'顺序,必须为数字'
        else:
            menuitem.name=request.POST.get('name').strip()
            if id:
                menuitem.index=indexnum
            menuitem.save()
            cache.delete(MENU_ALL_LIST+str(site.get('id')))

    viewmap['msg']=msg
#    viewmap['menulist']=Menu.objects.filter(site=site.get('id')).filter(link=None).order_by('index')
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def webinfo(site,request):
    if 'POST'!=request.method.upper():
#        raise Http404()
#        return HttpResponse(json.dumps({'ss':544}))
        return HttpResponseRedirect('/blog/Admin')
    viewmap={}
    webname=request.POST.get('webname','')
    keyword=request.POST.get('keyword','')
    desc=request.POST.get('desc','')
    websiteinfo=WebSiteInfo.objects.get(pk=site.get('id',0))
    if websiteinfo:
        websiteinfo.name=webname
        websiteinfo.keywords=keyword
        websiteinfo.desc=desc
        websiteinfo.save()
        msg=u'保存成功'
        viewmap['msg']=msg
        cache.delete(site.get('webdomain'))
        site['webname']=webname
        site['desc']=desc
        site['keyword']=keyword
    ####################

    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def adminInfo(site,request):
    viewmap={}
    website=WebSiteInfo.objects.get(pk=site.get('id'))
    if website:
        bloguser=website.author
        if bloguser:
            userinfo={}
            userinfo['img']=bloguser.img
            userinfo['content']=bloguser.desc
            viewmap['adminInfo']=userinfo
    ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
#    menu(site,viewmap)
    return viewmap

def adminInfo_save(site,request):
    if 'POST'!=request.method.upper():
    #        raise Http404()
    #        return HttpResponse(json.dumps({'ss':544}))
        return HttpResponseRedirect('/blog/Admin/AdminInfo')
    viewmap={}
    website=WebSiteInfo.objects.get(pk=site.get('id'))
    if website:
        bloguser=website.author
        if bloguser:
            bloguser.desc=request.POST.get('content')
            msg=u'保存成功'
            f=request.FILES['pic']
            if f:
                if not isAllowFiles(f.name,["gif" , "png" , "jpg" , "jpeg" , "bmp"]):
                    msg=u'保存失败，图片格式不对。'
                elif not isAllowSize(f.size,220000) :
                    msg=u'保存失败，图片大小过大。'
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
                        traceback.print_exc()
                        if ufile.id:
                            ufile.delete()
                        msg=u'保存失败。'
                    else:
                        bloguser.img=UPLOAD_URL+str(site.get('id'))+'/'+newfilename
                        bloguser.save()
            else:
                bloguser.save()
            viewmap['msg']=msg
            userinfo={}
            userinfo['img']=bloguser.img
            userinfo['content']=bloguser.desc
            viewmap['adminInfo']=userinfo
    ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
#    menu(site,viewmap)
    return viewmap

def managePaper_save(site,request):
    viewmap={}
    if request.REQUEST.get('menuid'):
        viewmap['menu']=Menu.objects.get(pk=request.REQUEST.get('menuid'))
    else:
        viewmap['menu']=None
    if 'POST'==request.method.upper():
        editorValue=request.POST.get('papercontent','')
        title=request.POST.get('title','')
        menuid=request.POST.get('menuid')
        keyword=request.POST.get('keyword')
        desc=request.POST.get('desc')
        id=request.POST.get('id')
        if id:
            titlepaper=Title.objects.get(pk=id)
            if not titlepaper:
                titlepaper=Title()
            else:
                paperquery=Paper.objects.filter(title=titlepaper)[:1]
                if 0== len(paperquery):
                    paper=Paper()
                else:
                    paper=paperquery[0]
        else:
            titlepaper=Title()
            paper=Paper()

        titlepaper.title=title.strip()
        titlepaper.menu=viewmap['menu']

        titlepaper.desc=desc.strip()
        titlepaper.type='paper'
        titlepaper.author=request.user
        titlepaper.site=WebSiteInfo.objects.get(pk=site.get('id'))
        titlepaper.isPub=True
        titlepaper.save()
        titlepaper.keywords.clear()
        if keyword:
            website=WebSiteInfo.objects.get(pk=site.get('id'))
            keywordset=set(keyword.strip().split())
            keymap={}
            for k in keywordset:
                keymap[k.upper()]=k
            for key in Keyword.objects.filter(site=site.get('id')).filter(name__in=list(keywordset)):
                del keymap[key.name.upper()]
                titlepaper.keywords.add(key)
            for newkeyname in keymap.values():
                newkey=Keyword()
                newkey.name=newkeyname
                newkey.site=website
                newkey.save()
                titlepaper.keywords.add(newkey)
            titlepaper.save()
        paper.title=titlepaper
        paper.content=editorValue.strip()
        paper.contentnotag=strip_tags(editorValue)
        paper.save()

        msg=u'保存成功'
        viewmap['msg']=msg
#        titlepaper.papercontent='dsasfad'
#        titlepaper.keyword=keyword
        viewmap['paper']=titlepaper
        fromurl=request.POST.get('fromurl')
        if fromurl:
            msgid=str(uuid.uuid4())
            cache.set(msgid,u'修改文章《%s》成功。'%(titlepaper.title,),60)
#            response.set_cookie("msg",msgid,30)
            if fromurl.find('?')!=-1:
                fromurl+='&msgid='+msgid
            else:
                fromurl+='?msgid='+msgid
            return HttpResponseRedirect(fromurl)
#        viewmap['editorValue']=editorValue


    else:
        paperid=request.GET.get('paperid')
        if paperid:
            titlepaper=Title.objects.get(pk=paperid)
            viewmap['paper']=titlepaper
            if hasattr(request,'environ'):
                viewmap['fromurl']=request.environ.get('HTTP_REFERER','')
            if hasattr(request,'META'):
                viewmap['fromurl']=request.META.get('HTTP_REFERER','')
    ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap


def managePaperImage_save(site,request):
    viewmap={}
    if request.REQUEST.get('menuid'):
        viewmap['menu']=Menu.objects.get(pk=request.REQUEST.get('menuid'))
    else:
        viewmap['menu']=None
    if 'POST'==request.method.upper():
        title=request.POST.get('title','')
        menuid=request.POST.get('menuid')
        keyword=request.POST.get('keyword')
        desc=request.POST.get('desc')
        id=request.POST.get('titleid')
        if id:
            titlepaperquery=Title.objects.filter(site=site.get('id')).filter(pk=id)[:1]
            if 1== len(titlepaperquery):
                titlepaper=titlepaperquery[0]
            else:
                titlepaper=Title()

        else:
            titlepaper=Title()

        titlepaper.title=title.strip()
        titlepaper.menu=viewmap['menu']

        titlepaper.desc=desc.strip()
        titlepaper.type='image'
        titlepaper.author=request.user
        titlepaper.site=WebSiteInfo.objects.get(pk=site.get('id'))
        titlepaper.isPub=True
        titlepaper.save()
        titlepaper.keywords.clear()
        if keyword:
            website=WebSiteInfo.objects.get(pk=site.get('id'))
            keywordset=set(keyword.strip().split())
            for key in Keyword.objects.filter(site=site.get('id')).filter(name__in=list(keywordset)):
                keywordset.remove(key.name)
                titlepaper.keywords.add(key)
            for newkeyname in keywordset:
                newkey=Keyword()
                newkey.name=newkeyname
                newkey.site=website
                newkey.save()
                titlepaper.keywords.add(newkey)
            titlepaper.save()
        result={'result':True,'id':titlepaper.id}
        return HttpResponse(json.dumps(result))


    else:
        paperid=request.GET.get('paperid')
        if paperid:
            titlepaper=Title.objects.get(pk=paperid)
            viewmap['paper']=titlepaper
            if hasattr(request,'environ'):
                viewmap['fromurl']=request.environ.get('HTTP_REFERER','')
            if hasattr(request,'META'):
                viewmap['fromurl']=request.META.get('HTTP_REFERER','')
        ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def delImageInfoByImgId(site,request):
    imgid=request.POST.get('imgid')
    if imgid:
        pimg=PaperImage.objects.get(pk=imgid)
#        import os
#        if os.path.isfile(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.img):
#            os.remove(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.img)
#        if os.path.isfile(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.imgsmall):
#            os.remove(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.imgsmall)
#        if os.path.isfile(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.imgmid):
#            os.remove(UPLOAD_ROOT+str(site.get('id'))+'/'+pimg.imgmid)
        pimg.delete()
        return HttpResponse(imgid)

def getImageListByTitleId(site,request):
    titleid=request.POST.get('titleid','')
    if titleid:
        titlequery=Title.objects.filter(site=site.get('id')).filter(pk=titleid)[:1]
        title=None
        if 1==len(titlequery):
            title=titlequery[0]
        if title and  title.type in SWFUPLOAD_TITLE_TYPE:
            from xml.dom.minidom import Document
            xml=Document()
            datas=xml.createElement('datas')
            xml.appendChild(datas)
            for img in PaperImage.objects.filter(title=title).order_by('index'):
                data=xml.createElement('data')
                data.setAttribute('imgid',str(img.id))
                data.setAttribute('imgsrc',img.getImgUrl(site.get('id')))
                data.setAttribute('imgindex',str(img.index))
                data.setAttribute('imgtext',img.content)
                datas.appendChild(data)
            return HttpResponse(xml.toxml('utf-8'))
    return HttpResponse()

def saveImageInfoByTitleId(site,request):
    titleid=request.POST.get('titleid','')
    if titleid:
        titlequery=Title.objects.filter(site=site.get('id')).filter(pk=titleid)[:1]
        title=None
        if 1==len(titlequery):
            title=titlequery[0]
        if title and  title.type in SWFUPLOAD_TITLE_TYPE:
            from xml.dom.minidom import Document
            xml=Document()
            datas=xml.createElement('datas')
            datas.setAttribute('userid',str(request.user.pk))
            xml.appendChild(datas)
            for i in range(0,int(request.POST.get('num'))):
                id=request.POST.get('id'+str(i))
                if id:
                    paperImage=PaperImage.objects.get(pk=id)
                else:
                    paperImage=PaperImage()
                    paperImage.img=''
                    paperImage.imgmid=''
                    paperImage.imgsmall=''
                paperImage.title=title
                paperImage.content=request.POST.get('text'+str(i))
                paperImage.index=int(request.POST.get('index'+str(i)))
                paperImage.save()

                data=xml.createElement('data')
                data.setAttribute('imgid',str(paperImage.id))
                data.setAttribute('imgindex',str(paperImage.index))
                datas.appendChild(data)
            return HttpResponse(xml.toxml('utf-8'))
    return HttpResponse()

def managePaperImage_upload(site,request):
    '''
    http://blog.csdn.net/jbgtwang/article/details/6454023
    '''
    f=request.FILES['imgfile']
    parser=ImageFile.Parser()
    for chunk in f.chunks():
        parser.feed(chunk)
    img=parser.close()
    newfilename=''
    ufile=UeditorFile()
    try:
        newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/','big'+f.name)
        ufile.filename=f.name
        ufile.realfilename=newfilename
        ufile.size=f.size
        ufile.title=request.POST.get('pictitle','')
        ufile.type='image'
        ufile.site=WebSiteInfo.objects.get(pk=site.get('id'))
        ufile.user=User.objects.get(pk=request.GET.get('userid'))
        ufile.save()
        paperImage=PaperImage.objects.get(pk=request.REQUEST.get('imgid'))
        w,h=img.size
        if f.name.split('.')[-1].lower()!='gif':
            if w>PAPERIMAGE_SIZE_WIDTH_BIG:
                nw=int(w*((PAPERIMAGE_SIZE_WIDTH_BIG*1.0)/(w*1.0)))
                nh=int(h*((nw*1.0)/(w*1.0)))
                img=img.resize((nw,nh))
                w=nw
                h=nh
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            else:
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            paperImage.img=newfilename

            ####
            newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/','mid'+newfilename)
            if w>PAPERIMAGE_SIZE_WIDTH_MID:
                nw=int(w*((PAPERIMAGE_SIZE_WIDTH_MID*1.0)/(w*1.0)))
                nh=int(h*((nw*1.0)/(w*1.0)))
                img=img.resize((nw,nh))
                w=nw
                h=nh
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            else:
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            paperImage.imgmid=newfilename
            ####
            newfilename=getSaveName(UPLOAD_ROOT+str(site.get('id'))+'/','small'+newfilename)
            if h>PAPERIMAGE_SIZE_HEIGH_SMALL:
                nh=int(h*((PAPERIMAGE_SIZE_HEIGH_SMALL*1.0)/(h*1.0)))
                nw=int(w*((nh*1.0)/(h*1.0)))
                img=img.resize((nw,nh))
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            else:
                img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            paperImage.imgsmall=newfilename
        else:
            img.save(UPLOAD_ROOT+str(site.get('id'))+'/'+newfilename)
            paperImage.img=newfilename
            paperImage.imgmid=newfilename
            paperImage.imgsmall=newfilename
        paperImage.save()
    except Exception,e:
        ufile.delete()
        return Http404()
    return HttpResponse()

def managePaper_list(site,request):
    viewmap={}
    msgid=request.GET.get('msgid')
    if msgid:
        viewmap['msg']=cache.get(msgid)
        cache.delete(msgid)
    menuid=request.GET.get('menuid')
    if menuid:
        viewmap['menu']=Menu.objects.get(pk=request.REQUEST.get('menuid'))
    paperid=request.GET.get('paperid')
    if paperid:
        try:
            delpaper=Title.objects.get(pk=paperid)
        except :
            msg=u'文章已不存在。'
        else:
            msg=u'删除文章《'+delpaper.title+u'》成功.'
            delpaper.delete()
        viewmap['msg']=msg

    offset=request.GET.get('offset','0')
    offset=int(offset)
    offsetN=offset+PAPER_LIST_LIMIT
    offsetP=(offset>=PAPER_LIST_LIMIT and [offset-PAPER_LIST_LIMIT] or [0])[0]

    paperquery=Title.objects.filter(site=site.get('id',0)).filter(menu=int(menuid)).filter(isPub=True).order_by('-updateDate')
    totalpaper=paperquery.count()
    if totalpaper<offsetN:
        offsetN-=PAPER_LIST_LIMIT
    viewmap['paperlist']=paperquery[offset:offset+PAPER_LIST_LIMIT]
    viewmap['offset']=offset
    viewmap['offsetN']=offsetN
    viewmap['offsetP']=offsetP

    pagelist=[]
    pp=offset-(PAPER_LIST_LIMIT*4)
    nn=offset+(PAPER_LIST_LIMIT*4)
    for p in range(0,completePage(totalpaper,PAPER_LIST_LIMIT)):
        if p*PAPER_LIST_LIMIT> pp and p*PAPER_LIST_LIMIT<nn:
            pagelist.append({'page':p+1,'offset':p*PAPER_LIST_LIMIT})
    viewmap['lastpage']=p*PAPER_LIST_LIMIT
    viewmap['pagelist']=pagelist

     ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def manageAlbum_save(site,request):
    viewmap={}
    albummenu=Menu.objects.filter(site=site.get('id')).filter(type='album')[:1]
    if len(albummenu)==0:
        albummenu=Menu()
        albummenu.name='相册'
        albummenu.index=0
        albummenu.type='album'
        albummenu.site=WebSiteInfo.objects.get(pk=site.get('id'))
        albummenu.save()
    else:
        albummenu=albummenu[0]
    viewmap['albummenu']=albummenu
    if 'POST'==request.method.upper():
        albumname=request.POST.get('albumName',u'未命名')
        albumid=request.POST.get('albumId',None)
        if albumid:
            album=Title.objects.get(pk=albumid)
        else:
            album=Title()
        album.title=albumname
        album.menu=albummenu
        album.type='album'
        album.author=request.user
        album.site=WebSiteInfo.objects.get(pk=site.get('id'))
        album.isPub=True
        album.save()
        viewmap['album']=album
        msg=u'保存成功'
        viewmap['msg']=msg
    else:
        albumid=request.GET.get('albumId',None)
        if albumid:
            album=Title.objects.get(pk=albumid)
            viewmap['album']=album
     ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap
def manageAlbum_upload(site,request):
    viewmap={}
    if 'GET'==request.method.upper():
        albumid=request.GET.get('albumId',None)
        if albumid:
            album=Title.objects.get(pk=albumid)
            viewmap['album']=album
     ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap


def manageAlbum_list(site,request):
    viewmap={}
    albummenu=Menu.objects.filter(site=site.get('id')).filter(type='album')[:1]
    if len(albummenu)==0:
        albummenu=Menu()
        albummenu.name='相册'
        albummenu.index=0
        albummenu.type='album'
        albummenu.site=WebSiteInfo.objects.get(pk=site.get('id'))
        albummenu.save()
    else:
        albummenu=albummenu[0]
    viewmap['album']=albummenu
    titlequery=Title.objects.filter(menu=albummenu)
    albumlist=[]
    for album in titlequery:
        firstImageList=PaperImage.objects.filter(title=album).order_by('index')[:1]
        if 0==len(firstImageList):
            album.firstImage=None
        else:
            album.firstImage=firstImageList[0]
            album.firstImage.imgsmal=album.firstImage.getImgUrlsmall(site.get('id'))
        albumlist.append(album)

    viewmap['albumlist']=albumlist
     ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap


def paperShow(site,request,menuid,paperid,index=1):
    viewmap={}
    msgid=request.GET.get('msgid')
    if msgid:
        viewmap['msg']=cache.get(msgid)
        cache.delete(msgid)
#    paperid=request.GET.get('paperid')
    if menuid and paperid:
        try:
            menuitem=Menu.objects.get(pk=menuid)
            paper=Title.objects.get(pk=paperid)
            paper.replyNum=Replay.objects.filter(title=paper).count()
        except :
            raise  Http404()
        else:
            viewmap['title']=paper
            viewmap['menu']=menuitem
            #### 设置左侧数据
            left(site,viewmap)
            #### 设置 menu 数据
            menu(site,viewmap)
            if 'paper'==paper.type:
                viewmap['templateNo']=0
            elif 'image'==paper.type:
                viewmap['templateNo']=1
                if not index:
                    index=1
                viewmap['index']=int(index)
                l=[]
                hdp=[]
                for img in PaperImage.objects.filter(title=paper).order_by('index'):
                    l.append({'id':img.id,'index':img.index,'content':img.content,'img':img.getImgUrl(site.get('id')),'imgsmall':img.getImgUrlsmall(site.get('id')),'imgmid':img.getImgUrlmid(site.get('id'))})
                    hdp.append({'href':img.getImgUrl(site.get('id')),'title':img.content})
                viewmap['paperimglist']=l
                viewmap['hdpjson']=json.dumps(hdp)
                viewmap['totalimg']=len(l)
    else:
        raise Http404()

    return viewmap

def albumShow(site,request,menuid,paperid,index=1):
    viewmap={}
    msgid=request.GET.get('msgid')
    if msgid:
        viewmap['msg']=cache.get(msgid)
        cache.delete(msgid)
#    paperid=request.GET.get('paperid')
    if menuid and paperid:
        try:
            menuitem=Menu.objects.get(pk=menuid)
            paper=Title.objects.get(pk=paperid)
            paper.replyNum=Replay.objects.filter(title=paper).count()
        except :
            raise  Http404()
        else:
            viewmap['title']=paper
            viewmap['menu']=menuitem
            #### 设置左侧数据
            left(site,viewmap)
            #### 设置 menu 数据
            menu(site,viewmap)

            if not index:
                index=1
            viewmap['index']=int(index)
            l=[]
            hdp=[]
            for img in PaperImage.objects.filter(title=paper).order_by('index'):
                l.append({'id':img.id,'index':img.index,'content':img.content,'img':img.getImgUrl(site.get('id')),'imgsmall':img.getImgUrlsmall(site.get('id')),'imgmid':img.getImgUrlmid(site.get('id'))})
                hdp.append({'href':img.getImgUrl(site.get('id')),'title':img.content})
            viewmap['paperimglist']=l
            viewmap['hdpjson']=json.dumps(hdp)
            viewmap['totalimg']=len(l)
    else:
        raise Http404()

    return viewmap
def column(site,request,menuid):
    viewmap={}
    if menuid:
        menuid=int(menuid)
        viewmap['menu']=Menu.objects.get(pk=menuid)
        viewmap['titlename']=viewmap['menu'].name
    offset=request.GET.get('offset','0')
    offset=int(offset)
    offsetN=offset+PAPER_LIST_LIMIT
    offsetP=(offset>=PAPER_LIST_LIMIT and [offset-PAPER_LIST_LIMIT] or [0])[0]

    paperquery=Title.objects.filter(site=site.get('id',0)).filter(menu=int(menuid)).filter(isPub=True).order_by('-updateDate')
    totalpaper=paperquery.count()
    if totalpaper<offsetN:
        offsetN-=PAPER_LIST_LIMIT
    viewmap['paperlist']=paperquery[offset:offset+PAPER_LIST_LIMIT]
    viewmap['offset']=offset
    viewmap['offsetN']=offsetN
    viewmap['offsetP']=offsetP

    pagelist=[]
    pp=offset-(PAPER_LIST_LIMIT*4)
    nn=offset+(PAPER_LIST_LIMIT*4)
    for p in range(0,completePage(totalpaper,PAPER_LIST_LIMIT)):
        if p*PAPER_LIST_LIMIT> pp and p*PAPER_LIST_LIMIT<nn:
            pagelist.append({'page':p+1,'offset':p*PAPER_LIST_LIMIT})
    viewmap['lastpage']=p*PAPER_LIST_LIMIT
    viewmap['pagelist']=pagelist

    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)

    return viewmap

def keywords(site,request):
    viewmap={}
    keyword=request.GET.get('keyword','')
    if keyword:
        keyword=int(keyword)
    viewmap['keyword']=Keyword.objects.get(pk=keyword)
    viewmap['titlename']=viewmap['keyword'].name
    offset=request.GET.get('offset','0')
    offset=int(offset)
    offsetN=offset+PAPER_LIST_LIMIT
    offsetP=(offset>=PAPER_LIST_LIMIT and [offset-PAPER_LIST_LIMIT] or [0])[0]

    paperquery=Title.objects.filter(site=site.get('id',0)).filter(keywords=keyword).filter(isPub=True).order_by('-updateDate')
    totalpaper=paperquery.count()
    if totalpaper<offsetN:
        offsetN-=PAPER_LIST_LIMIT
    viewmap['paperlist']=paperquery[offset:offset+PAPER_LIST_LIMIT]
    viewmap['offset']=offset
    viewmap['offsetN']=offsetN
    viewmap['offsetP']=offsetP

    pagelist=[]
    pp=offset-(PAPER_LIST_LIMIT*4)
    nn=offset+(PAPER_LIST_LIMIT*4)
    for p in range(0,completePage(totalpaper,PAPER_LIST_LIMIT)):
        if p*PAPER_LIST_LIMIT> pp and p*PAPER_LIST_LIMIT<nn:
            pagelist.append({'page':p+1,'offset':p*PAPER_LIST_LIMIT})
    viewmap['lastpage']=p*PAPER_LIST_LIMIT
    viewmap['pagelist']=pagelist

    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)

    return viewmap

def paperlist(site,request):
    viewmap={}
    menulist=[]
    menuquery=Menu.objects.filter(site=site.get('id')).filter(type='paper').filter(link=None).order_by('index')
    for m in menuquery:
        m.totalcount=Title.objects.filter(menu=m).count()
        paperlist=[]
        paperquery=Title.objects.filter(menu=m).filter(isPub=True).order_by('-releaseDate')[:5]
        for paper in paperquery:
            paperlist.append(paper)
        m.paperlist=paperlist
        menulist.append(m)
    viewmap['menus']=menulist
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def albumlist(site,request,albumid=None):
    viewmap={}
    albummenu=None
    if albumid:
        albumid=int(albumid)
        albummenu=Menu.objects.get(pk=albumid)
    if not albummenu:
        albummenu=Menu.objects.filter(site=site.get('id')).filter(type='album')[:1]
        if len(albummenu)==0:
            albummenu=Menu()
            albummenu.name='相册'
            albummenu.index=0
            albummenu.type='album'
            albummenu.site=WebSiteInfo.objects.get(pk=site.get('id'))
            albummenu.save()
        else:
            albummenu=albummenu[0]
    viewmap['album']=albummenu
    titlequery=Title.objects.filter(menu=albummenu)

    offset=request.GET.get('offset','0')
    offset=int(offset)
    offsetN=offset+ALBUM_LIST_LIMIT
    offsetP=(offset>=ALBUM_LIST_LIMIT and [offset-ALBUM_LIST_LIMIT] or [0])[0]
    totalpaper=titlequery.count()
    if totalpaper<offsetN:
        offsetN-=ALBUM_LIST_LIMIT
    viewmap['albumlist']=titlequery[offset:offset+ALBUM_LIST_LIMIT]
    viewmap['offset']=offset
    viewmap['offsetN']=offsetN
    viewmap['offsetP']=offsetP
    pagelist=[]
    pp=offset-(ALBUM_LIST_LIMIT*4)
    nn=offset+(ALBUM_LIST_LIMIT*4)
    for p in range(0,completePage(totalpaper,ALBUM_LIST_LIMIT)):
        if p*ALBUM_LIST_LIMIT> pp and p*ALBUM_LIST_LIMIT<nn:
            pagelist.append({'page':p+1,'offset':p*ALBUM_LIST_LIMIT})
    viewmap['lastpage']=p*ALBUM_LIST_LIMIT

    albumlist=[]
    for album in viewmap['albumlist']:
        firstImageList=PaperImage.objects.filter(title=album).order_by('index')[:1]
        if 0==len(firstImageList):
            album.firstImage=None
        else:
            album.firstImage=firstImageList[0]
            album.firstImage.imgsmal=album.firstImage.getImgUrlsmall(site.get('id'))
        albumlist.append(album)

    viewmap['albumlist']=albumlist
     ####################
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    return viewmap

def commentList(site,request):
    viewmap={}
    titleid=request.POST.get('titleid')
    if titleid:
        titleid=int(titleid)
    paperid=request.POST.get('paperid')
    if paperid:
        paperid=int(paperid)
    else:
        paperid=0
    commentlist(site,viewmap,titleid,paperid)
    return HttpResponse(json.dumps(viewmap['commentlist']))


def commentAdd(site,request):

    if hasattr(request,'environ'):
        fromurl=request.environ.get('HTTP_REFERER','/')
    if hasattr(request,'META'):
        fromurl=request.META.get('HTTP_REFERER','/')
    imagecode=request.POST.get('imagecode','')
    if imagecode!=request.session['imgcode']:
        msgid=str(uuid.uuid4())
        cache.set(msgid,u'验证码错误',60)
        if fromurl.find('?')==-1:
            fromurl+='?msgid='+msgid
        else:
            fromurl+='&msgid='+msgid
    else:
        type=request.POST.get('type','email')
        contact=request.POST.get('contact','')
        guest=None
        if contact:
            guestquery=Guest.objects.filter(site=site.get('id')).filter(type=type).filter(contact=contact)[:1]
            if 1==len(guestquery):
                guest=guestquery[0]
                guest.nickname=request.POST.get('nickname','游客')
                guest.save()
            else:
                guest=Guest()
                guest.contact=contact
                guest.type=type
                guest.nickname=request.POST.get('nickname','游客')
                guest.site=WebSiteInfo.objects.get(pk=site.get('id'))
                guest.save()
            request.session['guest']=guest
        titleid=request.POST.get('titleid','')
        title=None
        if titleid:
            title=Title.objects.get(pk=titleid)
        paperid=request.POST.get('paperid',0)
        if paperid:
            paperid=int(paperid)
        replayid=request.POST.get('commentid',0)
        fatherreplay=None
        if replayid:
            fatherreplay=Replay.objects.get(pk=replayid)
        if title and paperid:
            replay=Replay()
            replay.title=title
            replay.content=request.POST.get('comment','')
            replay.paperid=paperid
            replay.fatherid=fatherreplay
            replay.guest=guest
            replay.face=request.POST.get('face','1')
            replay.site=WebSiteInfo.objects.get(pk=site.get('id'))
            replay.isPub=True
            replay.save()

    return HttpResponseRedirect(fromurl)


def papercount(site,request):
    '''
    查询阅读次数和留言次数
    '''
    titleid=request.POST.get('titleid')
    if titleid:
        titlequery=Title.objects.filter(pk=titleid)
        titlelist=titlequery[:1]
        if 1==len(titlelist) and site.get('id')==titlelist[0].site_id:
            titlequery.update(showNum=titlelist[0].showNum+1)
            paperid=request.POST.get('paperid')
            if paperid:
                paperid=int(paperid)
            else:
                paperid=0
            replaycount=Replay.objects.filter(title=titlelist[0]).filter(paperid=paperid).count()
            return HttpResponse(json.dumps({'success':True,'showNum':titlelist[0].showNum+1,'replayNum':replaycount}))
    return Http404()

def websiteNum(site,request):
    '''
    网站访问次数
    '''
    if hasattr(request,'environ'):
        domain=request.environ['HTTP_HOST']
    if hasattr(request,'META'):
        domain=request.META['HTTP_HOST']
    website=WebSiteDomain.objects.filter(site=site.get('id')).filter(domain=domain)
    if 1==website.count():
        web=website[0]
        website.update(showNum=web.showNum+1)
        return HttpResponse(json.dumps({'success':True,'showNum':web.showNum+1}))
    else:
        return Http404()

def emailSubscribe(site,request):
    '''
    博客邮件订阅
    '''
    viewmap={}
    #### 设置左侧数据
    left(site,viewmap)
    #### 设置 menu 数据
    menu(site,viewmap)
    email=request.POST.get('email','')
    fromurl=request.POST.get('fromurl','')
    if not fromurl:
        if hasattr(request,'environ'):
            fromurl=request.environ.get('HTTP_REFERER','')
        if hasattr(request,'META'):
            fromurl=request.META.get('HTTP_REFERER','')
    success=False
    flag=False
    form=EmailSubscribe(request.POST)
    if form.is_valid():
        smquery=SubscribeMail.objects.filter(site=site.get('id')).filter(email=email)
        if 0==smquery.count():
            s=SubscribeMail()
            s.site=WebSiteInfo.objects.get(pk=site.get('id'))
            s.email=email
            s.save()

            success=True
            flag=False
        else:
            smquery.delete()
            success=True
            flag=True
        viewmap['subscribmail']={'success':success,'flag':flag,'fromurl':fromurl,'email':email}

    else:
        viewmap['subscribmail']={'success':success,'flag':flag,'fromurl':fromurl,'email':email}
    return viewmap

def picshow(site,request):
    '''
    首页滚动图片
    '''
    picShow=picShow[0].tag
    img=''
    for p in ImageFiles().all().filter('tag =',picShow).order('-updateTime'):
        img+='<a href="/pic/%s/%s.html"><img src="/pics/s/%s/0/170" class="imgmarg"  height="170px"></a>' %(str(p.key()),str(p.tag),str(p.key()))
    js=""" var mar=document.getElementById('picshow');mar.innerHTML='%s';
    """%(img,)
    self.response.out.write(js)


def page404(site,viewmap):
    return {}