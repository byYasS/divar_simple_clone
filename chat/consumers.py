from channels.generic.websocket import WebsocketConsumer
from chat.models import ListingConversation, ListingMessage
from django.core.files.base import ContentFile
from asgiref.sync import async_to_sync
from django.db.models import Q
from uuid import uuid4
from io import BytesIO
from PIL import Image
from django.utils import timezone
from . import presence as p
import struct
import json


MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}


def time_format(dt):
    if timezone.is_aware(dt):
        time = timezone.localtime(dt)
    return time.strftime("%H:%M")


def user_is_allowed(user):
    if ListingConversation.objects.filter(Q(seller=user) | Q(customer=user)).exists():
        return True
    else:
        return False


class ConversationConsumer(WebsocketConsumer):
    
    def send_message(self, data):
        user = self.scope["user"]
        message = data["message"]
        conversation_id = data["conversation_id"]
        
        conversation = ListingConversation.objects.get(id=conversation_id)
        created_message = ListingMessage.objects.create(sender=user, conversation=conversation, content=message)
        
        self.notification(created_message)
            
        message_data = {
            "sender_name":created_message.sender.username,
            "message":message,
            "sended_at":time_format(created_message.sended_at)
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
                "image_url": old_message.image.url if old_message.image else None,
                "sended_at":time_format(old_message.sended_at)
            })
            
            
        self.chat_message(messages_data)
        
    
    def handle_image(self, bytes_data):
    
        try:
            header_len = struct.unpack(">I", bytes_data[:4])[0]
            header = json.loads(bytes_data[4:4 + header_len])
            image_bytes = bytes_data[4 + header_len:]
        except (struct.error, ValueError):
            return self.send_error("پیام نامعتبر است.")

        if header.get("request") != "send_image":
            return self.send_error("درخواست نامعتبر است.")

 
        if not image_bytes or len(image_bytes) > MAX_IMAGE_SIZE:
            return self.send_error("حجم تصویر نامعتبر است (حداکثر ۵ مگابایت).")


        try:
            img = Image.open(BytesIO(image_bytes))
            img.verify()
            ext = ALLOWED_FORMATS.get(img.format)
        except Exception:
            ext = None

        if ext is None:
            return self.send_error("فقط تصاویر JPG، PNG، WEBP و GIF مجاز هستند.")

        caption = str(header.get("message", ""))[:1000]
        conversation = ListingConversation.objects.get(id=header.get("conversation_id"))
        user = self.scope["user"]

        msg = ListingMessage(conversation=conversation, sender=user, content=caption if caption else None)
        msg.image.save(f"{uuid4().hex}.{ext}", ContentFile(image_bytes), save=True)

        message_data = {
            "sender_name": user.username,
            "message": msg.content,
            "image_url": msg.image.url,
            "sended_at": time_format(msg.sended_at)
        }

        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,        
            {"type": "chat_message",
            "response":"send_new_message",  
            "message_data": message_data},
        )
    
    
    def send_error(self, text):
        self.send(text_data=json.dumps(
            {"event": {"response": "error", "error": text}}
        ))
    

    def connect(self):
        conversation = self.scope["url_route"]["kwargs"]["conversation_id"]
        
        self.room_name = f"{conversation}"
        self.room_group_name = f"chat_{self.room_name}"
        
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        
        if user_is_allowed(self.scope["user"]):
            self.accept()
        else:
            self.close()
            return
        
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
    
    
    def receive(self, text_data = None, bytes_data = None):
        if bytes_data:
            self.handle_image(bytes_data)
            return
        
        json_text_data = json.loads(text_data)
        
        if json_text_data["request"] == "send_new_message":
            self.send_message(json_text_data)
            
        elif json_text_data["request"] == "get_old_messages":
            self.get_messages_history(json_text_data)
        
        
    def notification(self, new_message):
        conversation = new_message.conversation
        sender = new_message.sender
      
        if sender.id == conversation.seller_id:
            recipient = conversation.customer
        else:
            recipient = conversation.seller
    
        notification_data = {
            "conversation_id": conversation.id,
            "sender_name": sender.username,
            "listing_title": conversation.listing.title,
            "message": new_message.content or "تصویر ",
            "sended_at": time_format(new_message.sended_at)
        }
        
        async_to_sync(self.channel_layer.group_send)(f"user_{recipient.id}", {
            "type": "notification_message",
            "notification_data": notification_data,
        })    
        
        
    def chat_message(self, event):
        self.send(text_data=json.dumps({
            "event":event,
            "user_id":self.scope["user"].id,
        }))
        
          
        
class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope["user"]
        self.group_name = None

        if not user.is_authenticated:
            self.close()
            return

        self.group_name = f"user_{user.id}"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        
        self.accept()

    def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name, self.channel_name
            )

    def notification_message(self, event):
        self.send(text_data=json.dumps({
            "event": {
                "response": "new_notification",
                "notification_data": event["notification_data"],
            }
        })) 
        
             
             
class PresenceConsumer(WebsocketConsumer):
    
    def connect(self):
        user = self.scope["user"]
       
        if not user.is_authenticated:
            self.close()
            return
        
        self.group_name = f"presence_{user.id}"
        
        self.user_id = user.id
        self.connection_id = self.channel_name
        
        p.add_connection(self.user_id, self.connection_id)
        
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        
        self.accept()
        
    def disconnect(self, code):
        user_id = self.user_id
        connection_id = self.channel_name

        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        
        p.remove_connection(user_id, connection_id)
        
    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("request") != "get_status":
            return

        conversation_id = data.get("conversation_id")

        if not conversation_id:
            return

        user = self.scope["user"]

        conversation = ListingConversation.objects.filter(
            id=conversation_id
        ).filter(
            Q(seller=user) | Q(customer=user)
        ).first()

        if not conversation:
            self.send(text_data=json.dumps({
                "event": "presence_status",
                "error": "conversation_not_found",
            }))
            return

        if conversation.seller_id == user.id:
            partner = conversation.customer
        else:
            partner = conversation.seller

        self.send(text_data=json.dumps({
            "event": "presence_status",
            "user_id": partner.id,
            "status": "online" if p.is_online(partner.id) else "offline",
        }))  
        
    
    