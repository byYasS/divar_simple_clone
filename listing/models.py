from django.db import models
from account.models import User
from location.models import City

# Create your models here.
def category_icon_path(instance, filename):
    return f"categories/{instance.name}/{filename}"

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.FileField(upload_to=category_icon_path, null=True)
    
    class Meta:
        verbose_name="category"
        verbose_name_plural="categories"
        
        
    def __str__(self):
        return self.name
  
    
    
class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    price = models.DecimalField(max_digits=9, decimal_places=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name="listings")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.title} - {self.seller}" 
    
    
    
def listing_image_path(instance, filename):
    return f"listing/{instance.listing.id}/{filename}"


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="image")
    image = models.ImageField(upload_to=listing_image_path)
    
    
    def __str__(self):
        return f"{self.listing} images"
    
    
    
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmark")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bookmark")
      
    def __str__(self):
        return self.listing.title    
