from django.shortcuts import redirect
from django.urls import resolve


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request, *args, **kwds):
        current_url_name = resolve(request.path_info).url_name
        
        if not request.user.is_authenticated:
            public_urls = [
                "send_otp",
                "verify_otp",
                "login",
                "list_page",
                "search",
                "category"
            ]
            
            if current_url_name not in public_urls:
                return redirect("/account/register/")
            
        return self.get_response(request)
        
        