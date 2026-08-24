from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def register_required(view_function):
    
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        
        if request.user.is_authenticated:
            return view_function(request, *args, **kwargs)
        
        register_url = reverse("account:send_otp")
        
        return redirect(register_url)
    
    return wrapper
        
        