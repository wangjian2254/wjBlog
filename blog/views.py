#coding=utf-8
# Create your views here.

from django.template.context import RequestContext


from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from wjBlog.util.tool import render_to_response_custom, domain_site


def edit(request):
    user=request.user
    return render_to_response_custom(request,'adminedit.html',locals())

@domain_site
def index(fun_name,site,request):
    '''
    博客首页
    '''
    return render_to_response_custom(fun_name,site,request)

@login_required
@domain_site
def blogAdmin(fun_name,site,request):
    '''
    博客管理界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def manageMenu(fun_name,site,request):
    '''
    博客栏目界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def manageMenu_save(fun_name,site,request):
    '''
    博客栏目界面 保存
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def webinfo(fun_name,site,request):
    '''
    博客信息修改操作
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def AdminInfo(fun_name,site,request):
    '''
    博客用户个人简介界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))


@login_required
@domain_site
def AdminInfo_save(fun_name,site,request):
    '''
    博客用户个人简介信息修改操作
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def managePaper_save(fun_name,site,request):
    '''
    博文操作界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def managePaperImage_save(fun_name,site,request):
    '''
    博文操作界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@csrf_exempt
@domain_site
def getImageListByTitleId(fun_name,site,request):

    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@csrf_exempt
@domain_site
def saveImageInfoByTitleId(fun_name,site,request):

    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

#@login_required
@csrf_exempt
@domain_site
def managePaperImage_upload(fun_name,site,request):

    '''
    博文操作界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@csrf_exempt
@domain_site
def delImageInfoByImgId(fun_name,site,request):

    '''
    博文操作界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def managePaper_list(fun_name,site,request):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))

@login_required
@domain_site
def manageAlbum_list(fun_name,site,request):
    '''
       博客相册列表操作界面
       '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))


@login_required
@domain_site
def manageAlbum_save(fun_name,site,request):
    '''
       博客相册操作界面
       '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))


@login_required
@domain_site
def manageAlbum_upload(fun_name,site,request):
    '''
       博客相册操作界面
       '''
    return render_to_response_custom(fun_name,site,request,context_instance=RequestContext(request))


@domain_site
def column(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@domain_site
def paper(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))


@domain_site
def albumshow(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@domain_site
def paperlist(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@domain_site
def albumlist(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@domain_site
def keywords(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@domain_site
def commentAdd(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))

@csrf_exempt
@domain_site
def commentList(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))
@csrf_exempt
@domain_site
def papercount(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))
@csrf_exempt
@domain_site
def websiteNum(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))
@csrf_exempt
@domain_site
def emailSubscribe(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))
@csrf_exempt
@domain_site
def picshow(fun_name,site,request,*arg):
    '''
    博文列表操作界面
    '''
    return render_to_response_custom(fun_name,site,request,*arg,context_instance=RequestContext(request))