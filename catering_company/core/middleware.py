from django.utils.deprecation import MiddlewareMixin
from core.signals import set_current_user

class CurrentUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        return None
    
    def process_response(self, request, response):
        set_current_user(None)
        return response