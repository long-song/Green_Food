# 定义索引类
from haystack import indexes
# 导入模型类
from integral_app.models import Pro_sku
#指定对于某个类的某些数据建立索引
# 索引类名格式：模型类名+Index
class ProSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # document=True说明text是一个索引字段
    # use_template=True：根据表中哪些字段建立索引文件，把说明放到一个文件中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """
        返回你的模型类
        :return:
        """
        return Pro_sku

    def index_queryset(self, using=None):
        """
        返回建立索引的数据
        :param using:
        :return:
        """
        return self.get_model().objects.all()

