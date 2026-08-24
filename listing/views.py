from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Listing, ListingImage, Bookmark
from account.decorators import register_required
from django.db import transaction
from .forms import ListingForm
import json


# Create your views here.
def validate_images(images):
    valid_image_formats= ["image/jpeg", "image/jpg", "image/png"]
    valid_image_size = 5 * 1024 * 1024
    errors = []
    
    for image in images:
        
        if image.size > valid_image_size:
            errors.append("حجم تصویر نباید بیشتر از 5 مگابایت باشد")
                                                        
        if image.content_type not in valid_image_formats:
            errors.append("فرمت تصویر معتبر نیست")
        
    return errors 
    
    
    
def listing_page(request):
    listings =  Listing.objects.all()
    return render(request, "list.html", {"listings":listings})



@register_required
def listing_detail(request, id):
    listing = Listing.objects.get(id=id)
    images = ListingImage.objects.filter(listing=listing)
    
    if listing.seller == request.user:
        is_seller = True
    else:
        is_seller = False
        
    if Bookmark.objects.filter(user=request.user, listing=listing).exists():
        is_bookmarked = True
    else:
        is_bookmarked = False        
    
    return render(request, "detail.html", {"listing":listing, "images":images, "is_seller":is_seller, "is_bookmarked":is_bookmarked})



@register_required
@transaction.atomic
def create_listing(request):
    
    if request.user.profile.city is None:
        return redirect("/account/user/profile/edit/")
    else:
        city = request.user.profile.city
        
    if request.method == "POST":
        form = ListingForm(request.POST)
        uploading_image_errors = []
        
        if form.is_valid():
            if request.FILES:
                images = request.FILES.getlist("images")
                
                if len(images) > 10:
                   uploading_image_errors.append("حداکثر 10 تصویر قابل بارگذاری است") 
                    
                uploading_image_errors.extend(validate_images(images))
                           
            else:
                uploading_image_errors.append("حداقل 1 تصویر باید بارگذاری شود")  
                     
            if len(uploading_image_errors) > 0:
                return render(request, "create_listing.html", {"form":form, "errors":uploading_image_errors})  
                                  
            cd = form.cleaned_data
            
            listing = Listing.objects.create(
                title=cd["title"],
                description=cd["description"],
                price=cd["price"],
                category=cd["category"],
                seller=request.user,
                city=city)
            
            
            for image in images:
                ListingImage.objects.create(listing=listing, image=image)

                         
            return redirect("/account/user/listings/")         
    else:
        form = ListingForm()
        return render(request, "create_listing.html", {"form":form})
    
 
 
@register_required 
@transaction.atomic    
def update_listing(request, id):
    
    listing = get_object_or_404(Listing, id=id, seller=request.user)
    images = ListingImage.objects.filter(listing=listing)
    updating_image_errors = []
    context = {}
    
    if request.method == "POST":
        deleted_image_ids = json.loads(request.POST.get("deleted_images"))
            
        form = ListingForm(request.POST, instance=listing)
        new_images = []
        
        if form.is_valid():
            if request.FILES:
                new_images = request.FILES.getlist("images")
                images_count = images.count()
                current_total =  images_count - len(deleted_image_ids) + len(new_images) 
                
                if current_total > 10:
                    updating_image_errors.append("تعداد تصاویر نباید بیشتر از 10 عدد باشد")
                elif current_total == 0:
                    updating_image_errors.append("حداقل 1 تصویر باید بارگذاری شود")
                          
                updating_image_errors.extend(validate_images(new_images))   
                            
            remaining_images = images.exclude(id__in=deleted_image_ids)
            context = {
                "form":form,
                "errors":updating_image_errors,
                "images":remaining_images,
                "edit_mode":True
            }
            
            if len(updating_image_errors) > 0:
                return render(request, "update_listing.html", context)
            
            form.save()
            
            images_to_delete = ListingImage.objects.filter(id__in=deleted_image_ids, listing=listing)
            
            for image in images_to_delete:
                image.image.delete(save=False)
                image.delete()
                    
            for image in new_images:
                ListingImage.objects.create(listing=listing, image=image)
                                
            return redirect(f"/listings/{id}/")     
    else:
        form = ListingForm(instance=listing)
        
    context.pop("errors", None)
    context["images"] = images

    return render(request, "update_listing.html", context)
     
  
  
@register_required    
def delete_listing(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=id, seller=request.user)
        
        listing_images = ListingImage.objects.filter(listing=listing)
        
        for image in listing_images:
            image.image.delete(save=False)
            image.delete()
            
        listing.delete()
        
    return HttpResponse("آگهی شما با موفقیت حذف شد")



@register_required
def toggle_bookmark(request, id):
    listing = Listing.objects.get(id=id)
    bookmark = Bookmark.objects.filter(listing=listing, user=request.user).first()
        
    if bookmark:
        bookmark.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(user=request.user, listing=listing)
        bookmarked=True
        
    return JsonResponse({"bookmarked":bookmarked})


