from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from chat.models import ListingConversation, ListingMessage
from django.db.models import Q
import json


class ConversationConsumer(WebsocketConsumer):
    
    def send_message(self, data):
        user = self.scope["user"]
        message = data["message"]
        conversation_id = data["conversation_id"]
        
        conversation = ListingConversation.objects.get(id=conversation_id)
        created_message = ListingMessage.objects.create(sender=user, conversation=conversation, content=message)
        
            
        message_data = {
            "sender_name":created_message.sender.username,
            "message":message,
            "sended_at":created_message.sended_at.isoformat()[11:16],
        }
        
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            "type":"chat_message",
            "response":"send_new_message",
            "message_data":message_data,
        })
        


    def get_messages_history(self, data):
        conversation_id = data["conversation_id"]
        
        conversation = ListingConversation.objects.get(id=conversation_id)
        
        old_messages = ListingMessage.objects.filter(conversation=conversation).order_by("-sended_at")

        messages_data = []
        
        for old_message in old_messages:
            
            messages_data.append({
                "sender_name":old_message.sender.username,
                "message":old_message.content,
                "sended_at":old_message.sended_at.isoformat()[11:16],
            })
            
            
        self.chat_message(messages_data)
        
    
    
    def connect(self):
        conversation = self.scope["url_route"]["kwargs"]["conversation_id"]
        
        self.room_name = f"{conversation}"
        self.room_group_name = f"chat_{self.room_name}"
        
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        
        
        if user_is_allowed(self.scope["user"]):
            self.accept()
        else:
            self.close()
        
        
        
    def disconnect(self):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
    
    
    
    def receive(self, text_data = None):
        json_text_data = json.loads(text_data)
        
        if json_text_data["request"] == "send_new_message":
            self.send_message(json_text_data)
            
        elif json_text_data["request"] == "get_old_messages":
            self.get_messages_history(json_text_data)
        
        
        
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "event":event,
            "user_id":self.scope["user"].id,
        }))
        
        
        
        
        
def user_is_allowed(user):
    if ListingConversation.objects.filter(Q(seller=user) | Q(customer=user)).exists():
        return True
    else:
        return False
    
    
    

            

        
    