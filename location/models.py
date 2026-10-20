from django.db import models

# Create your models here.
class Province(models.Model):
    name = models.CharField(verbose_name="نام", max_length=50, unique=True)
    
    class Meta:
        verbose_name = "استان"
        verbose_name_plural = "استان ها"
        
    def __str__(self):
        return self.name
    
    
      
class City(models.Model):
    name = models.CharField(verbose_name="نام", max_length=20)
    province = models.ForeignKey(Province, verbose_name="استان", on_delete=models.CASCADE, related_name="cities")
    
    class Meta:
        unique_together = ("province", "name")
        verbose_name = "شهر"
        verbose_name_plural = "شهر ها"
        
    def __str__(self):
        return self.name