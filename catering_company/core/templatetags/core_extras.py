# core/templatetags/core_extras.py
from django import template
from django.utils.safestring import mark_safe
import datetime

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    """Получает значение атрибута объекта, включая связанные объекты"""
    try:
        # Разделяем имя атрибута на части (для вложенных атрибутов)
        parts = attr_name.split('.')
        value = obj
        
        for part in parts:
            # Если текущее значение None, возвращаем None
            if value is None:
                return None
                
            # Пробуем получить атрибут
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                # Если нет атрибута, пробуем получить через get
                try:
                    value = value.get(part)
                except:
                    return None
                    
            # Если это callable (метод), вызываем его
            if callable(value):
                value = value()
        
        return value
    except (AttributeError, KeyError):
        return None

@register.filter
def is_foreign_key(value):
    """Проверяет, является ли значение связанным объектом"""
    if value is None:
        return False
    # Проверяем, что это объект модели Django
    return hasattr(value, '_meta') and hasattr(value._meta, 'model_name')

@register.filter
def is_date(value):
    """Проверяет, является ли значение датой/временем"""
    return isinstance(value, (datetime.datetime, datetime.date))

@register.filter
def is_boolean(value):
    """Проверяет, является ли значение булевым"""
    return isinstance(value, bool)

@register.filter(name='replace')
def replace(value, arg):
    """Заменяет символы в строке"""
    if not value:
        return value
    try:
        old, new = arg.split('|')
        return value.replace(old, new)
    except:
        return value

@register.simple_tag
def get_model_field_verbose_name(model_instance, field_name):
    """Получает человекочитаемое имя поля модели"""
    try:
        return model_instance._meta.get_field(field_name).verbose_name
    except:
        return field_name.replace('_', ' ').title()