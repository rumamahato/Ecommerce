from django.contrib import admin
from .models import *

admin.site.register(offerProduct)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.site_title="django project"
admin.site.site_header="Myshop"


class ProductAdminImage(admin.TabularInline):
    model=ProductImage
    extra=1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['id','name','price','category','desc']
    inlines=[ProductAdminImage]

