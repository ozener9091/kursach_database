def site_settings(request):
    """Контекстный процессор для настроек сайта"""
    font_size = request.session.get('font_size', 'normal')
    
    font_classes = {
        'small': 'font-small',
        'large': 'font-large',
        'xlarge': 'font-xlarge',
        'normal': ''
    }
    
    return {
        'current_font_class': font_classes.get(font_size, ''),
        'current_font_size': font_size,
    }

def theme_context_processor(request):
    return {
        'theme': request.session.get('theme', 'light'),
    }