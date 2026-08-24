from django.shortcuts import render, get_object_or_404, redirect
from listing.models import Listing
from .models import ListingConversation
from account.models import User
from django.db.models import Q
from account.decorators import register_required


# Create your views here.
@register_required
def user_conversations(request):
    conversations = ListingConversation.objects.filter(
        Q(seller=request.user) | Q(customer=request.user)
    )
    
    return render(request, "user_conversations.html", {"conversations":conversations})


def start_conversation(request, seller_name, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    seller = User.objects.get(username=seller_name)
    customer = request.user
    
    conversation = ListingConversation.objects.filter(listing=listing, seller=seller, customer=customer).first()
    
    if not conversation:
        conversation = ListingConversation.objects.create(listing=listing, seller=seller, customer=customer)
        
    return redirect("chat:conversation", conversation.id)
    
    
def conversation(request, conversation_id):
    conversation = ListingConversation.objects.get(id=conversation_id)

    return render(request, "conversation.html", {"conversation_id":conversation_id, "conversation":conversation})
    