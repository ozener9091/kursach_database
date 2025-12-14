from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(role_name, login_url=None):
    """
    Декоратор для проверки роли пользователя
    """
    def check_role(user):
        if user.is_authenticated:
            return user.groups.filter(name=role_name).exists()
        return False
    
    return user_passes_test(check_role, login_url=login_url)

def permission_required(perm, login_url=None):
    """
    Декоратор для проверки конкретного permission
    """
    def check_perm(user):
        if user.is_authenticated:
            return user.has_perm(perm)
        return False
    
    return user_passes_test(check_perm, login_url=login_url)

def director_required(view_func=None, login_url=None):
    actual_decorator = role_required('Директор', login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def manager_required(view_func=None, login_url=None):
    actual_decorator = role_required('Менеджер', login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def chef_required(view_func=None, login_url=None):
    actual_decorator = role_required('Шеф-повар', login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def hr_manager_required(view_func=None, login_url=None):
    actual_decorator = role_required('Менеджер по кадрам', login_url=login_url)
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def has_access_to_models(models, action='view'):
    """
    Декоратор для проверки доступа к группе моделей
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Требуется авторизация.')
                return redirect('login')
            
            for model in models:
                perm_codename = f'core.{action}_{model}'
                if not request.user.has_perm(perm_codename):
                    messages.error(request, f'У вас нет доступа к {model}.')
                    return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator