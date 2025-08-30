from django.http import HttpRequest
from django.shortcuts import redirect

def redirect_authenticated_user(view_func):
    def wrapper_func(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper_func