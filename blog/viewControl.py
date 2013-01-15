#coding=utf-8
# Create your views here.
import traceback
from django.core.cache import cache
TEMPLATE='template'
def viewByTemplate(funName,site):
    funMap=cache.get('templateTofun'+site.get(TEMPLATE,'None'))
    if not funMap:
        try:
            funmapmodule= __import__("wjBlog.blog.%s.funmap"%site.get(TEMPLATE),globals(),locals(),['fun_template'],-1)
            funMap=funmapmodule.fun_template()
        except Exception,e:
            traceback.print_exc()
#        if site.get(TEMPLATE,'None')=='default':
#            from wjBlog.blog.default.funmap import fun_template
#            funMap={}
#            funMap=fun_template()
        cache.set('templateTofun'+site.get(TEMPLATE,'None'),funMap,3600)
    fun,tem=funMap.get(funName,funMap.get('404'))
    return tem,fun
