#coding=utf-8
import urlparse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
#from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.contrib.auth import  login as auth_login

#cache.delete('scx'+str(s['id']))
#cache.set('allscx',result,60*60*2)
#cache.get('')
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from wjBlog.blog.models import WebSiteDomain, BlogUser
from wjBlog.blog.viewControl import viewByTemplate
from wjBlog import settings
from django.conf import settings as djangosettings




def domain_site(func):
    def test(request, *args, **kwargs):
        if hasattr(request,'environ'):
            domain=request.environ['HTTP_HOST']
        if hasattr(request,'META'):
            domain=request.META['HTTP_HOST']
        site=cache.get(domain)
        if not site:
            website=WebSiteDomain.objects.filter(domain=domain)[:1]
            if 1==len(website):
                website=website[0]
            else:
                ######  域名无效的情况
                return HttpResponseRedirect('http://www.zxxsbook.com')
            site={}
            site['id']=website.site_id
            site['webname']=website.site.name
            site['desc']=website.site.desc
            site['keyword']=website.site.keywords
            site['webdomain']=website.domain
            site['webdomainid']=website.id
            site['weburl']='http://'+website.domain
            site['template']=website.site.template.templatename
            cache.set(domain,site,settings.CACHE_TIMEOUT)
        return func(func.func_name,site,request, *args, **kwargs)
    return test

def render_to_response_custom(funName,site,request,*arg,**kwargs):
    tem,fun=viewByTemplate(funName,site)

    dictionary=fun(site,request,*arg)

    if not isinstance(dictionary,dict):
        return dictionary
    else:
        tem=tem[dictionary.get('templateNo',0)]
        if 'guest' in request.session:
            dictionary['guest']=request.session['guest']
    template=site.get('template')+tem
    ##############
    dictionary['webinfo']=site
    dictionary['user']=request.user
    return render_to_response(template,dictionary=dictionary,context_instance=kwargs.get('context_instance',None))



@csrf_protect
@never_cache
def login_blog(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)

        #修改登录代码，判断是否是域名的注册用户
        form.is_bloguser=False
        #domain=request.environ['HTTP_HOST']
        if hasattr(request,'environ'):
            domain=request.environ['HTTP_HOST']
        if hasattr(request,'META'):
            domain=request.META['HTTP_HOST']
        website=WebSiteDomain.objects.filter(domain=domain)[:1]
        if 1==len(website):
            website=website[0]
        else:
            website=None
        uquery=User.objects.filter(username=request.POST.get('username',''))[:1]
        if 1==len(uquery):
            tempuser=uquery[0]
        else:
            tempuser=None
        blogUserQuery=BlogUser.objects.filter(user=tempuser).filter(site=website)[:1]
        if 0==len(blogUserQuery):
            form.is_bloguser=True
        else:
            if form.is_valid():
                netloc = urlparse.urlparse(redirect_to)[1]

                # Use default setting if redirect_to is empty
                if not redirect_to:
                    redirect_to = djangosettings.LOGIN_REDIRECT_URL

                # Security check -- don't allow redirection to a different
                # host.
                elif netloc and netloc != request.get_host():
                    redirect_to = djangosettings.LOGIN_REDIRECT_URL

                # Okay, security checks complete. Log the user in.
                auth_login(request, form.get_user())

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)
        form.is_bloguser=False

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))


def completePage(total,size):
    if total%size==0:
        return total/size
    else:
        return total/size+1