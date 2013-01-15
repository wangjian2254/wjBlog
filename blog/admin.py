from wjBlog.blog.models import Ztperm, BlogUser, WebSiteInfo, WebSiteDomain, Templates

__author__ = 'Administrator'

from django.contrib import admin
admin.site.register(Ztperm)
admin.site.register(BlogUser)
admin.site.register(Templates)
admin.site.register(WebSiteInfo)
admin.site.register(WebSiteDomain)