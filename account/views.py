from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from .models import User, Profile
from .forms import EditProfileForm
from listing.models import Listing, Bookmark
from account.decorators import register_required
from . import otp
import re


# Create your views here.
def register_or_login(request, phone):
    user = User.objects.filter(phone_number=phone).first()
    if user:
        login(request, user)
    else:
        user = User.objects.create_user(phone_number=phone)
        user.save()
        login(request, user)
    

    
def normalization_phone(phone):
    phone = phone.strip()
    
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("98"):
        phone = "0" + phone[2:]
        
    return phone

      
      
def send_otp(request):
    message = ""
    
    if request.method == "POST":
        phone = request.POST.get("phone")
        phone_pattern = r"^(\+98|98|0)9\d{9}$"
        
        if phone:
            if re.fullmatch(phone_pattern, phone):
                normal_phone = normalization_phone(phone)
                otp.get_or_create_otp(normal_phone)
                request.session["phone"] = normal_phone
                
                return redirect("/account/register/verify/") 
            else:
                message = "شماره تلفن نامعتبر است"
        else:
            message = "لطفا شماره تلفن خود را وارد کنید"
        
    return render(request, "send_otp.html", {"message":message})
    
    
    
def verify_otp(request):
    message = ""
    phone = request.session.get("phone")
    ttl = otp.get_otp_ttl(phone)
    
    if request.method == "POST" and request.POST.get("code_request"):
        otp.resend_otp(phone)
        new_otp_ttl = otp.get_otp_ttl(phone)
        
        return JsonResponse({
            "success": True,
            "ttl": new_otp_ttl,
        })

    if request.method == "POST":
        received_otp = request.POST.get("otp")
        
        if received_otp:
            if otp.is_otp_valid(phone, received_otp):
                register_or_login(request, phone)
                otp.delete_otp(phone)
                del request.session["phone"]
                
                return redirect("/listings/")
            
            else:
                message = "کد وارد شده صحیح نیست"
        else:
            message = "لطفا کد تایید را وارد کنید"

    return render(request, "verify_otp.html",{"message": message, "ttl": ttl})

    
   
def logout_user(request):
    logout(request)
    
    return HttpResponse("شما با موفقیت از حساب کاربری خود خارج شدید") 
    
    
    
@register_required    
def user_profile(request):
    profile = Profile.objects.get(user=request.user)
    
    return render(request, "user_profile.html", {"profile":profile})



@register_required
def edit_profile(request):
    profile = request.user.profile
    
    data = {
        "username":request.user.username,
        "avatar":profile.avatar,
        "city":(lambda city : city if city else None)(profile.city)}
    
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cd = form.cleaned_data
            
            request.user.username = cd["username"]
            request.user.save()
            
            profile.avatar = cd["avatar"]
            profile.city = cd["city"]
            profile.save()
            
            return redirect("/account/user/profile/")
        
    else:
        form = EditProfileForm(initial=data)
            
    return render(request, "edit_profile.html", {"form":form})
        
            

@register_required
def user_listings(request):
    listings = Listing.objects.filter(seller=request.user)
    
    return render(request, "user_listings.html", {"listings":listings})



@register_required
def user_boomarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("listing")
    
    return render(request, "user_bookmarks.html", {"bookmarks":bookmarks})



    
    
    

        
    
    
    