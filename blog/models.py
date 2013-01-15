#coding=utf-8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class BlogUser(models.Model):
    user=models.ForeignKey(User)
    desc=models.TextField(null=True,blank=True,verbose_name=u'博客个人简介')
    img=models.CharField(max_length=200,null=True,blank=True,verbose_name=u'博客头像')
    site=models.ForeignKey('WebSiteInfo',null=True,blank=True,verbose_name=u'网站')
    class Admin():
        pass
    class Meta():
        verbose_name=u'博客使用者'
        unique_together = (('user', 'site'),)
    def __unicode__(self):
        return self.user.get_full_name()

class Templates(models.Model):
    name=models.CharField(max_length=50,verbose_name=u'模板名称')
    desc=models.CharField(max_length=300,null=True,blank=True,verbose_name=u'模板描述')
    templatename=models.CharField(max_length=20,verbose_name=u'模板路径')

    class Admin():
        pass
    class Meta():
        verbose_name=u'网站模板'
    def __unicode__(self):
        return self.name

class WebSiteInfo(models.Model):
    name=models.CharField(max_length=50,verbose_name=u'网站名称')
    desc=models.CharField(max_length=500,null=True,blank=True,verbose_name=u'网站简介',help_text=u'网站简介')
    keywords=models.CharField(max_length=200,null=True,blank=True,verbose_name=u'网站关键字',help_text=u'网站关键字')
    author=models.ForeignKey(BlogUser,related_name='author',verbose_name=u'博客隶属用户',help_text=u'博客显示谁的简介和头像？')
    replayEMail=models.ManyToManyField(BlogUser,verbose_name=u'网站有回复，被通知的用户')
    template=models.ForeignKey(Templates,verbose_name=u'网站采用的模板')
    class Admin():
        pass
    class Meta():
        verbose_name=u'网站信息'
    def __unicode__(self):
        return self.name

class WebSiteDomain(models.Model):
    domain=models.CharField(max_length=100,unique=True,verbose_name=u'网站域名')
    isDefault=models.BooleanField(default=True,verbose_name=u'是否默认网站域名')
    showNum=models.IntegerField(default=0,verbose_name=u'访问量')
    site=models.ForeignKey(WebSiteInfo)

    class Admin():
        pass
    class Meta():
        verbose_name=u'网站域名'
    def __unicode__(self):
        return '%s_%s'%(self.domain,self.site.name)

class Ztperm(models.Model):
    #
    perm={}
    class Meta:

        permissions=(
            ('blog_add',u'博客录入'),
            ('blog_update',u'博客修改'),
            ('image_add',u'图片上传'),
            ('image_update',u'图片修改'),
            )
    for code,codename in Meta.permissions:
        perm['ztmanage.'+code]=codename

class Guest(models.Model):
    contact=models.CharField(max_length=40,db_index=True,verbose_name=u'游客的联系方式',help_text=u'留言游客的联系方式')
    type=models.CharField(max_length=40,default='email',verbose_name=u'方式类型',help_text=u'email表示电子邮件、qq表示qq号、msn表示msn号、tel表示电话号')
    nickname=models.CharField(max_length=20,verbose_name=u'游客昵称',help_text=u'游客昵称')
    site=models.ForeignKey(WebSiteInfo)
    createDate=models.DateTimeField(auto_now_add=True,verbose_name=u'创建日期')
    lastLoginDate=models.DateTimeField(auto_now=True,verbose_name=u'修改日期')

    class Admin():
        pass
    class Meta():
        verbose_name=u'游客'
        unique_together = (('site', 'contact','type'),)
    def __unicode__(self):
        return self.nickname

class SubscribeMail(models.Model):
    site=models.ForeignKey(WebSiteInfo)
    email=models.EmailField(max_length=40,verbose_name=u'订阅的电子邮箱')
    class Admin():
        pass
    class Meta():
        verbose_name=u'订阅列表'
    def __unicode__(self):
        return self.email




class Keyword(models.Model):
    name=models.CharField(max_length=40,verbose_name=u'文章关键字')
    site=models.ForeignKey(WebSiteInfo)
    class Admin():
        pass
    class Meta():
        verbose_name=u'文章关键字'
    def __unicode__(self):
        return self.name

class Menu(models.Model):
    name=models.CharField(max_length=20,verbose_name=u'栏目')
    index=models.IntegerField(verbose_name=u'排序')
    fatherid=models.ForeignKey('Menu',null=True,blank=True,verbose_name=u'父级栏目')
    link=models.URLField(max_length=300,null=True,blank=True,verbose_name=u'指向链接',help_text=u'不算栏目，点击后直接按链接跳转')
    type=models.CharField(max_length=5,default='paper')
    site=models.ForeignKey(WebSiteInfo)
    class Admin():
        pass
    class Meta():
        verbose_name=u'栏目或分组'
    def __unicode__(self):
        return  '%s_%s'%(self.name,self.site.name)
    def url(self):
        return '/blog/%s.html'%(self.id,)

class Title(models.Model):
    title=models.CharField(max_length=200,verbose_name=u'文章标题')
    menu=models.ForeignKey(Menu,verbose_name=u'隶属栏目')
    keywords=models.ManyToManyField(Keyword,null=True,blank=True,verbose_name=u'文章关键字')
    desc=models.CharField(max_length=500,null=True,blank=True,verbose_name=u'导读、简介')
    type=models.CharField(max_length=5,verbose_name=u'类型',help_text=u'文章类型，文字、图集、调查')
    author=models.ForeignKey(User)
    showNum=models.IntegerField(default=0,verbose_name=u'阅读次数')
    fromPaper=models.ForeignKey('Title',related_name='zhuanzai',null=True,blank=True,verbose_name=u'转载文章',help_text=u'站内转载')
    fromurl=models.URLField(default=400,null=True,blank=True,verbose_name=u'转载文章链接',help_text=u'只要是转载，都会生成目标url')
    createDate=models.DateTimeField(auto_now_add=True,verbose_name=u'创建日期')
    updateDate=models.DateTimeField(auto_now=True,verbose_name=u'修改日期')
    releaseDate=models.DateTimeField(auto_now=True,verbose_name=u'发布日期')
    site=models.ForeignKey(WebSiteInfo)
    isPub=models.BooleanField(default=False,verbose_name=u'是否发布')
    staticurl=models.CharField(max_length=400,null=True,blank=True,verbose_name=u'静态url',help_text=u'生成静态网页时的路径')
    class Admin():
        pass
    class Meta():
        verbose_name=u'文章'
    def __unicode__(self):
        return self.title

    def getKeyword(self):
        l=[]
        for keyword in self.keywords.all():
            l.append(keyword.name)
        return ' '.join(l)
    def getKeywordList(self):
        l=[]
        for keyword in self.keywords.all():
            l.append(keyword)
        return l
    def url(self):
        if self.staticurl:
            return self.staticurl
        elif self.type in ['paper','image']:
            return '/blog/paper/%s/%s.html'%(self.menu_id,self.id)
        elif self.type =='album':
            return '/blog/album/%s/%s.html'%(self.menu_id,self.id)
    def getTypeStr(self):
        if self.type == 'paper':
            return u'[ 文章 ]'
        elif self.type =='image':
            return u'[ 幻灯片 ]'
        elif self.type =='album':
            return u'[ 相册 ]'


class Paper(models.Model):
    title=models.OneToOneField(Title,verbose_name=u'文章基础信息')
    content=models.TextField(verbose_name=u'文章内容')
    contentnotag=models.TextField(null=True,blank=True,verbose_name=u'文章纯净内容',help_text=u'去除html标签的文章内容')
    class Admin():
        pass
    class Meta():
        verbose_name=u'文本文章'
    def __unicode__(self):
        return self.title.title

class PaperImage(models.Model):
    title=models.ForeignKey(Title,verbose_name=u'文章基础信息')
    content=models.TextField(null=True,blank=True,verbose_name=u'图片内容')
    img=models.CharField(max_length=200,null=True,blank=True,verbose_name=u'图片')
    imgmid=models.CharField(max_length=200,null=True,blank=True,verbose_name=u'图片中等大小')
    imgsmall=models.CharField(max_length=200,null=True,blank=True,verbose_name=u'图片小图')
    index=models.IntegerField(default=0,verbose_name=u'图片排序')
    class Admin():
        pass
    class Meta():
        ordering=('index',)
        verbose_name=u'图集文章'
    def __unicode__(self):
        return self.title.title

    def getImgUrl(self,site):
        return '/static/upload/%s/%s'%(site,self.img)

    def getImgUrlsmall(self,site):
        return '/static/upload/%s/%s'%(site,self.imgsmall)

    def getImgUrlmid(self,site):
        return '/static/upload/%s/%s'%(site,self.imgmid)

class Replay(models.Model):
    title=models.ForeignKey(Title,verbose_name=u'隶属文章')
    face=models.CharField(max_length=5,default='1',verbose_name=u'留言表情')
    content=models.TextField(null=True,blank=True,verbose_name=u'留言内容')
    paperid=models.IntegerField(verbose_name=u'隶属的具体paper')
    createDate=models.DateTimeField(auto_now_add=True,verbose_name=u'创建日期')
    fatherid=models.ForeignKey('Replay',null=True,blank=True,verbose_name=u'对回复的回复')
    isAdmin=models.BooleanField(default=False,verbose_name=u'是否管理员回复')
    guest=models.ForeignKey(Guest,null=True,blank=True,verbose_name=u'游客',help_text=u'可以是匿名回复')
    admin=models.ForeignKey(User,null=True,blank=True,verbose_name=u'管理员',help_text=u'如果是管理员回复，则要记录是哪个管理员')
    site=models.ForeignKey(WebSiteInfo)
    isPub=models.BooleanField(default=False,verbose_name=u'是否发布',help_text=u'回复是否需要审核？')
    class Admin():
        pass
    class Meta():
        verbose_name=u'回复'
    def __unicode__(self):
        return self.title.title

    def paperUrl(self):
        if self.title.type=='paper':
            return self.title.url()
        elif self.title.type=='image':
            try:
                paperImage=PaperImage.objects.get(pk=self.paperid)
                return '/blog/paper/%s/%s_%s.html'%(self.title.menu_id,self.title_id,paperImage.index)
            except :
                return self.title.url()
        elif self.title.type=='album':
            try:
                paperImage=PaperImage.objects.get(pk=self.paperid)
                return '/blog/album/%s/%s_%s.html'%(self.title.menu_id,self.title_id,paperImage.index)
            except :
                return self.title.url()




