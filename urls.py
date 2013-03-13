from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import  logout
from wjBlog.util.tool import login_blog
from wjBlog.blog.views import edit,index
from wjBlog.util.imageCode import display
import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wjBlog.views.home', name='home'),
    # url(r'^wjBlog/', include('wjBlog.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^$',index),
    (r'^imagecode$',display),
    (r'^blog/',include('wjBlog.blog.urls')),

    (r'^accounts/login/$',login_blog,{'template_name':'login.html'}),
    (r'^accounts/logout/$', logout,{'template_name':'logout.html'}),
    (r'^accounts/profile/$',index),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ueditor/', include('wjBlog.ueditor.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    )
