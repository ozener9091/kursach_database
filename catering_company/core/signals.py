from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth import get_user_model
from .models import ActionLog
from django.apps import apps
import threading

User = get_user_model()

_thread_locals = threading.local()

def set_current_user(user):
    """Установить текущего пользователя для логирования"""
    _thread_locals.user = user

def get_current_user():
    """Получить текущего пользователя для логирования"""
    return getattr(_thread_locals, 'user', None)

def log_action(user, action, obj_type, obj_id, obj_name, request=None, details=None):
    """Функция для логирования действий"""
    if user:
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        ActionLog.objects.create(
            user=user,
            action=action,
            object_type=obj_type,
            object_id=obj_id,
            object_name=obj_name,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Логирование входа в систему"""
    log_action(
        user=user,
        action='login',
        obj_type='authentication',
        obj_id=None,
        obj_name='Вход в систему',
        request=request,
        details=f'Пользователь {user.username} вошел в систему'
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Логирование выхода из системы"""
    if user:
        log_action(
            user=user,
            action='logout',
            obj_type='authentication',
            obj_id=None,
            obj_name='Выход из системы',
            request=request,
            details=f'Пользователь {user.username} вышел из системы'
        )

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Логирование создания/изменения записей"""
    
    if sender._meta.app_label == 'core' and sender._meta.model_name != 'actionlog':
        user = get_current_user()
        if user:
            action = 'create' if created else 'update'
            obj_type = sender._meta.verbose_name_plural
            obj_name = str(instance)
            
            log_action(
                user=user,
                action=action,
                obj_type=obj_type,
                obj_id=instance.pk,
                obj_name=obj_name,
                details=f'{"Создание" if created else "Изменение"} записи'
            )

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Логирование удаления записей"""
    
    if sender._meta.app_label == 'core' and sender._meta.model_name != 'actionlog':
        user = get_current_user()
        if user:
            obj_type = sender._meta.verbose_name_plural
            obj_name = str(instance)
            
            log_action(
                user=user,
                action='delete',
                obj_type=obj_type,
                obj_id=instance.pk,
                obj_name=obj_name,
                details='Удаление записи'
            )