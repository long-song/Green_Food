from django.contrib import admin
from integral_app.models import Pro_sku,Group_buy,Reply_dis,Pro_discass,Pro_Type,Collect
# Register your models here.
admin.site.register(Pro_sku)
admin.site.register(Group_buy)
admin.site.register(Pro_Type)
admin.site.register(Pro_discass)
admin.site.register(Reply_dis)
admin.site.register(Collect)
