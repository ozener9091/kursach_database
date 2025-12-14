from django import template
from django.utils.safestring import mark_safe
import datetime

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    """Получает значение атрибута объекта, включая связанные объекты"""
    try:
        parts = attr_name.split('.')
        value = obj
        
        for part in parts:
            if value is None:
                return None
                
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                try:
                    value = value.get(part)
                except:
                    return None
                    
            if callable(value):
                value = value()
        
        return value
    except (AttributeError, KeyError):
        return None


@register.filter
def action_emoji(action):
    """Фильтр для получения эмодзи действия"""
    emojis = {
        'login': '🔓',
        'logout': '🔒',
        'create': '➕',
        'update': '✏️',
        'delete': '🗑️',
        'view': '👁️',
        'download': '📥',
        'export': '📤',
        'import': '📥',
        'print': '🖨️',
    }
    return emojis.get(action, '📝')