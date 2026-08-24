from django.contrib import admin
from .models import ListingConversation, ListingMessage


# Register your models here.
admin.site.register(ListingConversation)
admin.site.register(ListingMessage)