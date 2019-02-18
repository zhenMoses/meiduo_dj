from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer


from goods.models import SKU
from .search_indexes import SKUIndex

class SKUSerializer(serializers.ModelSerializer):
    """商品列表界面"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']




# class SKUSerializer(serializers.ModelSerializer):
#     """
#     SKU序列化器
#     """
#     class Meta:
#         model = SKU
#         fields = ('id', 'name', 'price', 'default_image_url', 'comments')

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')