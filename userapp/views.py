import os

import jsonpickle
from django.core.serializers import serialize
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from cartapp.cartmanager import SessionCartManager
from netshop.settings import BASE_DIR
from utils.code import gene_code, gene_text
from userapp.models import UserInfo, Area, Address


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        uname = request.POST.get('account', '')
        pwd = request.POST.get('password', '')
        # 注册用户信息
        try:
            user = UserInfo.objects.get(uname=uname, pwd=pwd)
            return render(request, 'register.html')
        except UserInfo.DoesNotExist:
            user = UserInfo.objects.create(uname=uname, pwd=pwd)
            # 将用户对象存入session中
            request.session['user'] = jsonpickle.dumps(user)
        return HttpResponseRedirect('/user/center/')


def CenterView(request):
    return render(request, 'center.html')


class LoginView(View):
    def get(self, request):
        reflag = request.GET.get('reflag', '')
        return render(request, 'login.html', {'reflag': reflag})

    def post(self, request):
        # 获取请求参数
        username = request.POST.get('account', '')
        password = request.POST.get('password', '')
        reflag = request.POST.get('reflag', '')
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        pwd = m.hexdigest()
        #判断是否登录成功
        user = UserInfo.objects.filter(uname=username, pwd=pwd)
        if user:
            request.session['user'] = jsonpickle.dumps(user[0])
            SessionCartManager(request.session).migrateSession2DB()

            if reflag == 'cart':
                return HttpResponseRedirect('/cart/queryAll/')

            return HttpResponseRedirect('/user/center/')
        return HttpResponseRedirect('/user/login/')


class LoadCodeView(View):
    def get(self,request):
        from captcha.image import ImageCaptcha
        image = ImageCaptcha(fonts=[os.path.join(BASE_DIR, 'utils', 'STXINWEI.TTF')])
        code = gene_text()
        imgObj = image.generate(code)
        #获取图片验证码
        # imgObj,code = gene_code()
        request.session['session_code'] = code
        return HttpResponse(imgObj, content_type='image/png')


class CheckCodeView(View):
    def get(self, request):
        # 获取请求参数
        code = request.GET.get('code',-1)
        # 获取session中生成的验证码
        session_code = request.session.get('session_code', -2)
        # 判断是否相等
        vflag = False
        if code == session_code:
            vflag = True
        # 返回响应
        return JsonResponse({'vflag': vflag})


class LogoutView(View):
    def post(self, request):
        # 清空session数据
        request.session.flush()
        return JsonResponse({'logout': True})


class AddressView(View):
    def get(self, request):
        #获取当前登录用户下的收货地址信息
        # 获取当前登录用户对象
        userstr = request.session.get('user', '')
        if userstr:
            user = jsonpickle.loads(userstr)
        addr_list = user.address_set.all()
        return render(request, 'address.html', {'addr_list': addr_list})

    def post(self, request):
        aname = request.POST.get('aname', '')
        aphone = request.POST.get('aphone', '')
        addr = request.POST.get('addr', '')
        # 获取当前对象
        userstr = request.session.get('user', '')
        if userstr:
            user = jsonpickle.loads(userstr)
        # 插入数据库表
        Address.objects.create(aname=aname, aphone=aphone, addr=addr, userinfo=user,
                               isdefault=(lambda count: True if count == 0 else False)(user.address_set.count()))
        return HttpResponseRedirect('/user/address/')


def loadAreaView(request):
    pid = request.GET.get('pid', -1)
    pid = int(pid)
    areaList = Area.objects.filter(parentid=pid)
    # 序列化数据
    jareaList = serialize('json', areaList)
    return JsonResponse({'jareaList': jareaList})


def updateDefaultAddrView(request):
    # 获取请求参数
    addrid = request.GET.get('addrid', '')
    addrid = int(addrid)
    Address.objects.filter(id=addrid).update(isdefault=True)
    Address.objects.exclude(id=addrid).update(isdefault=False)
    return HttpResponseRedirect('/user/address/')

