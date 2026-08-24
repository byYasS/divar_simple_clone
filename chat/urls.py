from django.urls import path
from . import views


app_name = "chat"

urlpatterns = [
    path("", views.user_conversations, name="user_conversations"),
    path("<str:seller_name>/<int:listing_id>/", views.start_conversation, name="start_chat"),
    path("<int:conversation_id>/", views.conversation, name="conversation"),
    
]
