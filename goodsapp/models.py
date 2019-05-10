from django.db import models

# Create your models here.
class Category(models.Model):
    """商品类别表"""
    # 类别名称
    cname = models.CharField(max_length=11)

    def __str__(self):
        return self.cname


class Goods(models.Model):
    """商品表"""
    # 商品名称
    gname = models.CharField(verbose_name='商品名称', max_length=100)
    gdesc = models.CharField(verbose_name='商品描述', max_length=100)
    oldprice = models.DecimalField(verbose_name='原价', max_digits=5, decimal_places=2)
    price = models.DecimalField(verbose_name='现价', max_digits=5, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='类别')

    def __str__(self):
        return self.gname

    def getImgUrl(self):
        return self.inventory_set.first().color.colorurl

    def getColor(self):
        colors = []
        for inventory in self.inventory_set.all():
            color = inventory.color
            if color not in colors:
                colors.append(color)
        return colors

    def getSizes(self):
        sizes = []
        for inventory in self.inventory_set.all():
            size = inventory.size
            if size not in sizes:
                sizes.append(size)
        return sizes

    def getDetailInfo(self):
        datas = {}
        for detail in self.goodsdetail_set.all():
            detailName = detail.getDname()
            if detailName not in datas:
                datas[detailName] = [detail.gdurl]
            else:
                datas[detailName].append(detail.gdurl)
        return datas

class GoodsDetailName(models.Model):
    """详情名称表"""
    gdname = models.CharField(max_length=30, verbose_name='详情名称')

    def __str__(self):
        return self.gdname


class GoodsDetail(models.Model):
    """商品详情表"""
    gdurl = models.ImageField(upload_to='', verbose_name='详情图片地址')
    detailname = models.ForeignKey(GoodsDetailName, )
    goods = models.ForeignKey(Goods, )

    def __str__(self):
        return self.detailname.gdname

    def getDname(self):
        return self.detailname.gdname


class Size(models.Model):
    """商品尺寸表"""
    sname = models.CharField(max_length=10, verbose_name='商品尺寸')

    def __str__(self):
        return self.sname


class Color(models.Model):
    """商品颜色"""
    colorname = models.CharField(max_length=10, verbose_name='颜色')
    colorurl = models.ImageField(upload_to='color/', verbose_name='颜色图片地址')

    def __str__(self):
        return self.colorname


class Inventory(models.Model):
    """库存表"""
    count = models.PositiveIntegerField(verbose_name='库存数量')
    color = models.ForeignKey(Color, )
    goods = models.ForeignKey(Goods, )
    size = models.ForeignKey(Size, )


