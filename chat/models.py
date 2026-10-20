from django.db import models
from listing.models import Listing
from account.models import User

# Create your models here.
class ListingConversation(models.Model):
    listing = models.ForeignKey(Listing, verbose_name="آگهی", on_delete=models.CASCADE, related_name="conversations")
    seller = models.ForeignKey(User, verbose_name="فروشنده", on_delete=models.CASCADE, related_name="conversations_as_seller")
    customer = models.ForeignKey(User, verbose_name="مشتری", on_delete=models.CASCADE, related_name="conversations_as_customer")
    created_at = models.DateTimeField(verbose_name="تاریخ شروع گفتگو", auto_now=False, auto_now_add=True)
    
    class Meta:
        verbose_name = "گفتگو"
        verbose_name_plural = "گفتگو ها"
        ordering = ["-created_at"]
 
                
    
    def __str__(self):
        return f"{self.listing} : {self.seller} - {self.customer}"
    
 
 
class ListingMessage(models.Model):
    sender = models.ForeignKey(User, verbose_name="فرستنده", on_delete=models.CASCADE, related_name="message_senders")
    conversation = models.ForeignKey(ListingConversation, verbose_name="گفتگو", on_delete=models.CASCADE, related_name="messages")
    content = models.CharField(verbose_name="محتوا", max_length=150, null=True, blank=True)
    image = models.ImageField(verbose_name="تصویر", upload_to="conversation/%Y/%m/", blank=True, null=True)
    sended_at = models.DateTimeField(verbose_name="تاریخ ارسال", auto_now=False, auto_now_add=True)
    
    class Meta:
        verbose_name = "پیام"
        verbose_name_plural = "پیام ها"
    
    def __str__(self):
        return f"{self.sender.username} - {self.conversation.listing.title}"
    
