from django.db import models
from account.models import User
from location.models import City

# Create your models here.
def category_icon_path(instance, filename):
    return f"categories/{instance.name}/{filename}"

class Category(models.Model):
    name = models.CharField(verbose_name="نام", max_length=50)
    icon = models.FileField(verbose_name="آیکون", upload_to=category_icon_path, null=True)
    
    class Meta:
        verbose_name="دسته بندی"
        verbose_name_plural="دسته بندی ها"
        
        
    def __str__(self):
        return self.name
  
    
    
class Listing(models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=50)
    description = models.TextField(verbose_name="توضیحات")
    seller = models.ForeignKey(User, verbose_name="فروشنده", on_delete=models.CASCADE, related_name="seller")
    price = models.DecimalField(verbose_name="قیمت", max_digits=9, decimal_places=0)
    category = models.ForeignKey(Category, verbose_name="دسته بندی", on_delete=models.CASCADE, related_name="listings")
    city = models.ForeignKey(City, verbose_name="شهر", on_delete=models.SET_NULL, related_name="listings", null=True)
    created_at = models.DateTimeField(verbose_name="تاریخ انتشار", auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="تاریخ ویرایش", auto_now=True, auto_now_add=False)
    
    class Meta:
        verbose_name = "آگهی"
        verbose_name_plural = "آگهی ها"
        ordering = ["-created_at"]
        
    
    def __str__(self):
        return f"{self.title} - {self.seller}" 
    
    
    
def listing_image_path(instance, filename):
    return f"listing/{instance.listing.id}/{filename}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, verbose_name="آگهی", on_delete=models.CASCADE, related_name="image")
    image = models.ImageField(verbose_name="تصویر", upload_to=listing_image_path)
    
    class Meta:
        verbose_name = "تصویر آگهی"
        verbose_name_plural = "تصاویر آگهی ها"
            
    def __str__(self):
        return f"{self.listing} images"
    
    
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, verbose_name="کاربر", on_delete=models.CASCADE, related_name="bookmark")
    listing = models.ForeignKey(Listing, verbose_name="آگهی", on_delete=models.CASCADE, related_name="bookmark")
      
    class Meta:
        verbose_name = "نشان"
        verbose_name_plural = "نشان ها"
            
    def __str__(self):
        return self.listing.title    
