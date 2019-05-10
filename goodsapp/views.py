import math

from django.core.paginator import Paginator
from django.http import HttpResponse

from django.shortcuts import render

# Create your views here.
from django.views import View

from goodsapp.models import Category, Goods


class IndexView(View):
    def get(self, request, categoryid=2, num=1):
        categoryid = int(categoryid)
        num = int(num)
        # 1、获取所有商品类别信息
        categoryList = Category.objects.all().order_by('id')
        # 2、获取某个类别下的所有商品信息
        goodsList = Goods.objects.filter(category_id=categoryid).order_by('id')
        # 3、分页功能
        paginatorObj = Paginator(object_list=goodsList, per_page=8)
        page_goods_obj = paginatorObj.page(num)
        # 4、页码数
        start = num - math.ceil(10/2)
        if start < 1:
            start = 1
        end = start + 9
        if end > paginatorObj.num_pages:
            end = paginatorObj.num_pages
        if end < 10:
            start = 1
        else:
            start = end - 9
        page_list = range(start, end)


        return render(request, 'index.html',{'categoryList': categoryList, 'goodsList': page_goods_obj, 'currentCid': categoryid, 'page_list':page_list})


def recommend(func):
    def _wrapper(detailView, request, goodsid, *args, **kwargs):
        # 获取cookie中的goodsid字符串
        c_goodsid = request.COOKIES.get('c_goodsid', '')
        # 存放浏览过的商品ID
        goodsIdList = [gid for gid in c_goodsid.split() if gid.strip()]
        # 存放浏览过的商品对象
        goodsObjList = [Goods.objects.get(id=gid) for gid in goodsIdList if gid != goodsid and Goods.objects.get(id=gid).category_id == Goods.objects.get(id=goodsid).category_id][:4]
        if goodsid in goodsIdList:
            goodsIdList.remove(goodsid)
            goodsIdList.insert(0, goodsid)
        else:
            goodsIdList.insert(0, goodsid)
        # 调用视图方法
        response = func(detailView, request, goodsid, recommend_list=goodsObjList, *args, **kwargs)
        # 将用户访问过的商品ID列表存放在cookie中
        response.set_cookie('c_goodsid', ' '.join(goodsIdList), max_age=3*24*60*60)
        return response
    return _wrapper




class DetailView(View):
    @recommend
    def get(self, request, goodsid, recommend_list=[]):
        goodsid = int(goodsid)
        try:
            goods = Goods.objects.get(id=goodsid)
            return render(request, 'detail.html', {'goods': goods, 'recommend_list':recommend_list})
        except Goods.DoesNotExist:
            return HttpResponse(status=404)

