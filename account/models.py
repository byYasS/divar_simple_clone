from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from location.models import City
import uuid


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره تلفن الزامی است")

        user = self.model(
            phone_number=phone_number,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, phone_number, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            phone_number,
            password,
            **extra_fields
        )
  
def generate_username():
    return f"کاربر_{uuid.uuid4().hex[:6]}" 
     
class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=50, default=generate_username, unique=True)
    verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = "phone_number"
    
    
    
    objects = UserManager()



def avatar_image_path(instance, filename):
    return f"profile/{instance.user.id}/{filename}"

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to=avatar_image_path, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, related_name="profiles", null=True, blank=True)
    

    def __str__(self):
        return self.user.username
    


    
    
    
    