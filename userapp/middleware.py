from django.shortcuts import redirect
from django.contrib import messages
from userapp.models import UserdetailsModel

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require authentication
        public_urls = [
            '/user-login/',
            '/user-register/',
            '/',
            '/user-contact/',
            '/admin-login/'
        ]

        # Check if the request URL requires authentication
        if request.path not in public_urls and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, 'Please login to continue')
                return redirect('user_login')
            else:
                # Attach the user object to the request
                try:
                    request.user = UserdetailsModel.objects.get(user_id=user_id)
                except UserdetailsModel.DoesNotExist:
                    # If user doesn't exist, clear session and redirect to login
                    request.session.flush()
                    messages.error(request, 'User session invalid. Please login again.')
                    return redirect('user_login')

        response = self.get_response(request)
        return response 