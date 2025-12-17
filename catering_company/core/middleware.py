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

class ThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем тему из сессии или куки
        if 'theme' in request.session:
            theme = request.session.get('theme', 'light')
        elif 'theme' in request.COOKIES:
            theme = request.COOKIES.get('theme', 'light')
        else:
            theme = 'light'
        
        # Добавляем тему в request
        request.theme = theme
        
        response = self.get_response(request)
        
        # Если тема установлена в сессии, устанавливаем куку
        if 'theme' in request.session:
            response.set_cookie('theme', request.session['theme'], max_age=30*24*60*60)
        
        return response