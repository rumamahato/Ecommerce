from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import CustomUser

# Create your models here.
class offerProduct(models.Model):
    title=models.CharField(max_length=200)
    desc= CKEditor5Field('Text', config_name='extends')
    price=models.DecimalField(max_digits=8,decimal_places=2)
    image=models.ImageField(upload_to="offerimages")
    is_available=models.BooleanField(default=True)
    create_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Category(models.Model):
    title=models.CharField(max_length=200)

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

class Product(models.Model):
    name = models.CharField(max_length=200)   # samsung s21
    category = models.ForeignKey(Category,on_delete=models.CASCADE)  # electronic
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    desc = CKEditor5Field('Text', config_name='extends')
    image = models.ImageField(upload_to="product-images")
    mark_price = models.DecimalField(max_digits=8, decimal_places=2)  # 100
    discount_percent = models.DecimalField(max_digits=4,decimal_places=2)  # 10
    price = models.DecimalField(max_digits=8,decimal_places=2,editable=False)  # 90
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    update_date=models.DateTimeField(auto_now=True)

    # 100 - (1-10/100) => 100 * (1-0.1) = 100 * 0.9 = 90

    def save(self,*args, **kwargs):
        self.name=self.name.capitalize()
        self.price = self.mark_price*(1-self.discount_percent/100)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    image=models.ImageField(upload_to="product-images")
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name="images")

    def __str__(self):
        return self.product.name

class Review(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name="reviews")
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback=models.TextField()
    rating=models.PositiveSmallIntegerField()
    created_at=models.DateTimeField(auto_now=True)

