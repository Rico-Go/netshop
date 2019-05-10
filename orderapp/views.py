import jsonpickle
from django.shortcuts import render

# Create your views here.
from cartapp.cartmanager import DBCartManger


def toOrderView(request):

    cartitems = request.GET.get('cartitems','')
    # 获取支付总金额
    totalPrice = request.GET.get('totalPrice','')

    # 判断当前用户是否登录
    if not request.session.get('user',''):
        return render(request, 'login.html', {'reflag': 'order','cartitems': cartitems, 'totalPrice': totalPrice})
    print(cartitems)
    cartitemList = jsonpickle.loads(cartitems)
    print(cartitemList)
    # 获取默认收货地址
    user = jsonpickle.loads(request.session.get('user',''))
    print(user)
    addrObj = user.address_set.get(isdefault=True)
    # 获取订单内容
    # [CartItem(),CartItem()]
    cartItemObjList = [DBCartManger(user).get_cartitems(**item) for item in cartitemList if item]

    return render(request, 'order.html', {'addrObj': addrObj, 'cartItemObjList': cartItemObjList, 'totalPrice': totalPrice})