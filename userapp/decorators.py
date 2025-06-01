from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "Please login first")
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view 