from django.db import models
from listing.models import Listing
from account.models import User

# Create your models here.
class ListingConversation(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="conversations")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_as_seller")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_as_customer")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.listing} : {self.seller} - {self.customer}"
    
    
class ListingMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_senders")
    conversation = models.ForeignKey(ListingConversation, on_delete=models.CASCADE, related_name="messages")
    content = models.CharField(max_length=150)
    sended_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username} - {self.conversation.listing.title}"