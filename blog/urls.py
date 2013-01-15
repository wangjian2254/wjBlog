#coding=utf-8
'''
Created on 2012-9-3

@author: 王健
'''
from django.conf.urls.defaults import patterns
from wjBlog.blog.views import picshow,emailSubscribe,websiteNum,albumshow,albumlist,manageAlbum_upload,manageAlbum_list,manageAlbum_save,papercount,getImageListByTitleId,delImageInfoByImgId,saveImageInfoByTitleId,managePaperImage_save,managePaperImage_upload,commentAdd,commentList,blogAdmin,manageMenu,webinfo,AdminInfo,AdminInfo_save,manageMenu_save,managePaper_save,managePaper_list,paper,column,paperlist,keywords
urlpatterns = patterns('^blog/$',
    (r'^Admin$',blogAdmin ),#博客管理界面
    (r'^Admin/manageMenu$',manageMenu ),#博文栏目管理界面
    (r'^Admin/manageMenu/save$',manageMenu_save ),#博文栏目修改
    (r'^Admin/webinfo$',webinfo ),#博客信息修改
    (r'^Admin/AdminInfo$',AdminInfo ),#博客个人信息管理界面
    (r'^Admin/AdminInfo/save$',AdminInfo_save ),#博客个人信息修改
    (r'^Admin/managePaper/save$',managePaper_save ),#博客文章保存
    (r'^Admin/managePaperImage/save$',managePaperImage_save ),#博客图片文章保存
    (r'^Admin/managePaperImage/upload$',managePaperImage_upload ),#博客图片文章保存
    (r'^Admin/getImageListByTitleId$',getImageListByTitleId ),#博客图片文章保存
    (r'^Admin/saveImageInfoByTitleId',saveImageInfoByTitleId ),#博客图片文章保存
    (r'^Admin/delImageInfoByImgId',delImageInfoByImgId ),#博客图片文章保存

    (r'^Admin/managePaper/list$',managePaper_list ),#博客文章列表
    (r'^paper/(\d+)/(\d+)[_]{0,1}(\d*).html$',paper ),#博客个人信息修改
    (r'^(\d+).html$',column ),#博客栏目列表
    (r'^keywords$',keywords ),#博客关键字列表
    (r'^paperlist.html$',paperlist ),#博客栏目列表
    (r'^albumlist.html$',albumlist ),#博客相册列表
    (r'^album/(\d+).html$',albumlist ),#博客相册列表
    (r'^album/(\d+)/(\d+)[_]{0,1}(\d*).html$',albumshow ),#博客相册列表

    (r'^Admin/manageAlbum/list',manageAlbum_list),#博客相册列表
    (r'^Admin/manageAlbum/save',manageAlbum_save),#博客相册修改
    (r'^Admin/manageAlbum/upload',manageAlbum_upload),#博客相册修改
    (r'^commentAdd',commentAdd),
    (r'^commentList',commentList),
    (r'^papercount$',papercount),
    (r'^websiteNum$',websiteNum),
    (r'^emailSubscribe.html$',emailSubscribe),
    (r'^picshow$',picshow),


)

