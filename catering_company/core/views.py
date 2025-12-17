
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.db import connection, models
from django.db.models import Count, Sum, Avg, F
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models.functions import TruncMonth, TruncDay
from django.apps import apps

from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')

from .models import *
from .forms import *
from .permissions import *
from .decorators import *
from .sql import *
import json


def help_page(request):
    """Страница справки"""
    return render(request, 'core/help.html')

def user_manual(request):
    """Руководство пользователя"""
    return render(request, 'core/user_manual.html')

def about_app(request):
    """О программе"""
    return render(request, 'core/about.html')

def miscellaneous_page(request):
    """Страница "Разное" """
    return render(request, 'core/miscellaneous.html')

@login_required
def home(request):
    """Домашняя страница"""
    return render(request, 'core/home.html', {'title': 'Главная страница'})

@login_required
def dashboard(request):
    """Панель управления"""

    context = {
        'title': 'Панель управления',
        'user': request.user,
        'recent_actions': ActionLog.objects.filter(user=request.user)[:10],
        'dish_count': Dish.objects.count(),
        'employee_count': Employee.objects.count(),
        'product_count': Product.objects.count(),
        'delivery_count': Delivery.objects.count(),
        'request_count': Request.objects.count(),
        'provider_count': Provider.objects.count(),
        'report_count': Report.objects.count(),
    }
    
    return render(request, 'core/dashboard.html', context)

def password_reset_request(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                
                new_password = 'password'
                
                user.set_password(new_password)
                user.save()
                
                subject = 'Восстановление пароля'
                message = f'''
                Здравствуйте,
                
                Ваш новый пароль: {new_password}
                
                Пожалуйста, измените его после входа в систему.
                
                С уважением,
                Администрация сайта
                '''
                
                from_email = 'noreply@localhost'
                
                send_mail(
                    subject,
                    message,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Новый пароль отправлен на ваш email. Пожалуйста, проверьте почту.')
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')
    else:
        form = PasswordResetForm()
    
    return render(request, 'core/password_reset.html', {'form': form})

@login_required
def director_tables(request):
    """Список всех таблиц для директора"""
    if not request.user.groups.filter(name='Директор').exists() and not request.user.is_superuser:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    
    app_models = apps.get_app_config('core').get_models()
    
    tables = []
    for model in app_models:
        model_name = model._meta.model_name
        verbose_name = model._meta.verbose_name_plural
        
        if model_name in ['abbreviationtype', 'gendertype', 'eventtype']:
            continue
            
        try:
            count = model.objects.count()
        except:
            count = 0
        
        url_name = f'table_{model_name}'
        
        tables.append({
            'name': model_name,
            'verbose_name': verbose_name,
            'count': count,
            'url': url_name,
            'has_view': request.user.has_perm(f'core.view_{model_name}'),
        })
    
    return render(request, 'core/role_tables.html', {
        'title': 'Все таблицы',
        'role': 'Директор',
        'tables': sorted(tables, key=lambda x: x['verbose_name']),
        'description': 'Полный доступ ко всем таблицам системы'
    })

@login_required
def manager_tables(request):
    """Список таблиц для менеджера"""
    if not request.user.groups.filter(name='Менеджер').exists() and not request.user.is_superuser:
        if not request.user.groups.filter(name='Директор').exists():
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('dashboard')
    
    manager_models = [
        ('dish', 'Блюда', Dish),
        ('ingredient', 'Ингредиенты', Ingredient),
        ('request', 'Заявки', Request),
        ('requestproduct', 'Продукты в заявках', RequestProduct),
        ('delivery', 'Поставки', Delivery),
        ('deliveryproduct', 'Продукты в поставках', DeliveryProduct),
        ('product', 'Продукты', Product),
        ('provider', 'Поставщики', Provider),
        ('report', 'Отчеты', Report),
        ('reportdish', 'Блюда в отчетах', ReportDish),
        ('bank', 'Банки', Bank),
        ('division', 'Подразделения', Division),
    ]
    
    tables = []
    for model_name, verbose_name, model in manager_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    reference_models = [
        ('country', 'Страны', Country),
        ('city', 'Города', City),
        ('street', 'Улицы', Street),
        ('unitofmeasurement', 'Единицы измерения', UnitOfMeasurement),
        ('assortmentgroup', 'Группы ассортимента', AssortmentGroup),
    ]
    
    for model_name, verbose_name, model in reference_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    return render(request, 'core/role_tables.html', {
        'title': 'Таблицы менеджера',
        'role': 'Менеджер',
        'tables': sorted(tables, key=lambda x: x['verbose_name']),
        'description': 'Управление меню, поставками и заявками'
    })

@login_required
def chef_tables(request):
    """Список таблиц для шеф-повара"""
    if not request.user.groups.filter(name='Шеф-повар').exists() and not request.user.is_superuser:
        if not request.user.groups.filter(name='Директор').exists():
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('dashboard')
    
    chef_models = [
        ('dish', 'Блюда', Dish),
        ('product', 'Продукты', Product),
        ('ingredient', 'Ингредиенты', Ingredient),
    ]
    
    tables = []
    for model_name, verbose_name, model in chef_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    reference_models = [
        ('assortmentgroup', 'Группы ассортимента', AssortmentGroup),
        ('unitofmeasurement', 'Единицы измерения', UnitOfMeasurement),
        ('country', 'Страны', Country),
        ('city', 'Города', City),
        ('street', 'Улицы', Street),
    ]
    
    for model_name, verbose_name, model in reference_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    return render(request, 'core/role_tables.html', {
        'title': 'Таблицы шеф-повара',
        'role': 'Шеф-повар',
        'tables': sorted(tables, key=lambda x: x['verbose_name']),
        'description': 'Просмотр меню и продуктов, редактирование ингредиентов'
    })

@login_required
def hr_tables(request):
    """Список таблиц для менеджера по кадрам"""
    if not request.user.groups.filter(name='Менеджер по кадрам').exists() and not request.user.is_superuser:
        if not request.user.groups.filter(name='Директор').exists():
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('dashboard')

    hr_models = [
        ('employee', 'Сотрудники', Employee),
        ('position', 'Должности', Position),
        ('placeofwork', 'Места работы', PlaceOfWork),
        ('department', 'Подразделения', Department),
        ('profession', 'Профессии', Profession),
        ('specialization', 'Специализации', Specialization),
        ('classification', 'Классификации', Classification),
        ('workbook', 'Трудовые книжки', WorkBook),
    ]
    
    tables = []
    for model_name, verbose_name, model in hr_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    reference_models = [
        ('country', 'Страны', Country),
        ('city', 'Города', City),
        ('street', 'Улицы', Street),
    ]
    
    for model_name, verbose_name, model in reference_models:
        try:
            count = model.objects.count()
            url_name = f'table_{model_name}'
            
            tables.append({
                'name': model_name,
                'verbose_name': verbose_name,
                'count': count,
                'url': url_name,
                'has_view': request.user.has_perm(f'core.view_{model_name}'),
            })
        except:
            continue
    
    return render(request, 'core/role_tables.html', {
        'title': 'Таблицы менеджера по кадрам',
        'role': 'Менеджер по кадрам',
        'tables': sorted(tables, key=lambda x: x['verbose_name']),
        'description': 'Управление персоналом и кадровыми данными'
    })

@login_required
def sql_query_page(request):
    """Страница для выполнения SQL SELECT запросов"""
    user = request.user
    
    available_models = get_available_models_for_user(user)
    
    template_queries = get_template_queries_for_user(user)
    
    if request.method == 'POST':
        if 'export' in request.POST:
            sql_query = request.POST.get('sql_query', '').strip()
            
            if not sql_query:
                messages.error(request, 'Введите SQL запрос для экспорта!')
                return render(request, 'core/sql_query.html', {
                    'available_models': available_models,
                    'template_queries': template_queries,
                    'sql_query': sql_query
                })
            
            return export_sql_results_to_excel(sql_query, user)
        
        sql_query = request.POST.get('sql_query', '').strip()
        
        if not is_valid_select_query(sql_query):
            messages.error(request, 'Разрешены только SELECT запросы!')
            return render(request, 'core/sql_query.html', {
                'available_models': available_models,
                'template_queries': template_queries,
                'sql_query': sql_query
            })
        
        if not is_query_using_allowed_tables(sql_query, available_models):
            messages.error(request, 'Запрос использует запрещенные таблицы!')
            return render(request, 'core/sql_query.html', {
                'available_models': available_models,
                'template_queries': template_queries,
                'sql_query': sql_query
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [col[0] for col in cursor.description]
                results = cursor.fetchall()
                
                return render(request, 'core/sql_query.html', {
                    'available_models': available_models,
                    'template_queries': template_queries,
                    'sql_query': sql_query,
                    'columns': columns,
                    'results': results,
                    'query_executed': True
                })
        except Exception as e:
            messages.error(request, f'Ошибка выполнения запроса: {str(e)}')
            return render(request, 'core/sql_query.html', {
                'available_models': available_models,
                'template_queries': template_queries,
                'sql_query': sql_query
            })
    
    return render(request, 'core/sql_query.html', {
        'available_models': available_models,
        'template_queries': template_queries
    })

@login_required
def update_theme(request):
    """Обновление темы через AJAX"""
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'light')
        
        # Сохраняем в сессии
        request.session['theme'] = theme
        
        # Также сохраняем в профиле пользователя, если нужно
        # request.user.profile.theme = theme
        # request.user.profile.save()
        
        return JsonResponse({'status': 'success', 'theme': theme})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def settings_page(request):
    """Страница настроек"""
    if request.method == 'POST':
        font_size = request.POST.get('font_size', 'normal')
        language = request.POST.get('language', 'ru')
        theme = request.POST.get('theme', 'light')
        
        request.session['font_size'] = font_size
        request.session['language'] = language
        request.session['theme'] = theme
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Настройки сохранены!'})
        else:
            messages.success(request, 'Настройки сохранены!')
            return redirect('settings')
    
    font_size = request.session.get('font_size', 'normal')
    language = request.session.get('language', 'ru')
    theme = request.session.get('theme', 'light')
    
    context = {
        'font_size': font_size,
        'language': language,
        'theme': theme,
    }
    return render(request, 'core/settings.html', context)

@login_required
def change_password(request):
    """Страница смены пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль успешно изменен!')
            return redirect('change_password')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {
        'form': form
    })

def generate_charts_data(user, start_date=None, end_date=None):
    """Генерирует данные для графиков с возможностью фильтрации по дате"""
    charts_data = []
    
    date_filter = {}
    if start_date:
        date_filter['date__gte'] = start_date
    if end_date:
        date_filter['date__lte'] = end_date
    
    if user.has_perm('core.view_dish') and user.has_perm('core.view_reportdish'):
        try:
            top_dishes_query = ReportDish.objects.select_related('report').values('dish__name')
            
            if start_date or end_date:
                top_dishes_query = top_dishes_query.filter(report__date__range=[start_date, end_date])
            
            top_dishes = top_dishes_query.annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]
            
            if top_dishes:
                dish_names = [item['dish__name'] for item in top_dishes if item['dish__name']]
                quantities = [float(item['total_quantity'] or 0) for item in top_dishes]
                
                charts_data.append({
                    'title': 'Топ-5 блюд по количеству продаж',
                    'chart_id': 'top_dishes_chart',
                    'chart_type': 'bar',
                    'x_data': dish_names,
                    'y_data': quantities,
                    'x_label': 'Блюда',
                    'y_label': 'Количество',
                    'color': 'skyblue'
                })
        except Exception as e:
            print(f"Error generating top dishes chart: {e}")
    
    if user.has_perm('core.view_dish') and user.has_perm('core.view_reportdish'):
        try:
            sales_by_group_query = ReportDish.objects.select_related('dish', 'dish__assortment_group', 'report').values(
                'dish__assortment_group__name'
            )
            
            if start_date or end_date:
                sales_by_group_query = sales_by_group_query.filter(report__date__range=[start_date, end_date])
            
            sales_by_group = sales_by_group_query.annotate(
                total_revenue=Sum(F('quantity') * F('dish__price'))
            ).order_by('-total_revenue')
            
            if sales_by_group:
                group_names = [item['dish__assortment_group__name'] for item in sales_by_group if item['dish__assortment_group__name']]
                revenues = [float(item['total_revenue'] or 0) for item in sales_by_group]
                
                charts_data.append({
                    'title': 'Выручка по группам ассортимента',
                    'chart_id': 'revenue_by_group_pie_chart',
                    'chart_type': 'pie',
                    'labels': group_names,
                    'values': revenues,
                    'color': 'lightgreen'
                })
        except Exception as e:
            print(f"Error generating revenue by group pie chart: {e}")
    
    if user.has_perm('core.view_product'):
        try:
            low_stock_products = Product.objects.filter(
                remaining_stock__lt=20
            ).order_by('remaining_stock')[:10]
            
            if low_stock_products:
                product_names = [p.name for p in low_stock_products]
                stock_levels = [float(p.remaining_stock) for p in low_stock_products]
                
                charts_data.append({
                    'title': 'Продукты с низким остатком',
                    'chart_id': 'low_stock_chart',
                    'chart_type': 'bar',
                    'x_data': product_names,
                    'y_data': stock_levels,
                    'x_label': 'Продукты',
                    'y_label': 'Остаток',
                    'color': 'orange'
                })
        except Exception as e:
            print(f"Error generating low stock chart: {e}")
    
    if user.has_perm('core.view_delivery'):
        try:
            deliveries_query = Delivery.objects.all()
            
            if start_date:
                deliveries_query = deliveries_query.filter(date__gte=start_date)
            if end_date:
                deliveries_query = deliveries_query.filter(date__lte=end_date)
        
            if not start_date and not end_date:
                start_date_calc = datetime.now() - timedelta(days=365)
                deliveries_query = deliveries_query.filter(date__gte=start_date_calc)
            
            monthly_deliveries = deliveries_query.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                delivery_count=Count('id')
            ).order_by('month')
            
            if monthly_deliveries:
                months = [item['month'].strftime('%Y-%m') for item in monthly_deliveries]
                counts = [item['delivery_count'] for item in monthly_deliveries]
                
                charts_data.append({
                    'title': 'Количество поставок по месяцам',
                    'chart_id': 'monthly_deliveries_chart',
                    'chart_type': 'line',
                    'x_data': months,
                    'y_data': counts,
                    'x_label': 'Месяц',
                    'y_label': 'Количество поставок',
                    'color': 'purple'
                })
        except Exception as e:
            print(f"Error generating deliveries chart: {e}")
    
    if user.has_perm('core.view_dish'):
        try:
            avg_price_by_group = Dish.objects.values(
                'assortment_group__name'
            ).annotate(
                avg_price=Avg('price')
            ).order_by('-avg_price')
            
            if avg_price_by_group:
                group_names = [item['assortment_group__name'] for item in avg_price_by_group if item['assortment_group__name']]
                avg_prices = [float(item['avg_price'] or 0) for item in avg_price_by_group]
                
                charts_data.append({
                    'title': 'Средняя цена блюд по группам',
                    'chart_id': 'avg_price_chart',
                    'chart_type': 'bar',
                    'x_data': group_names,
                    'y_data': avg_prices,
                    'x_label': 'Группы ассортимента',
                    'y_label': 'Средняя цена (₽)',
                    'color': 'coral'
                })
        except Exception as e:
            print(f"Error generating avg price chart: {e}")
    
    if user.has_perm('core.view_employee'):
        try:
            employees_by_position = Employee.objects.values(
                'position__name'
            ).annotate(
                employee_count=Count('id')
            ).order_by('-employee_count')
            
            if employees_by_position:
                position_names = [item['position__name'] for item in employees_by_position if item['position__name']]
                counts = [item['employee_count'] for item in employees_by_position]
                
                charts_data.append({
                    'title': 'Распределение сотрудников по должности',
                    'chart_id': 'employees_by_position_pie_chart',
                    'chart_type': 'pie',
                    'labels': position_names,
                    'values': counts,
                    'color': 'lightblue'
                })
        except Exception as e:
            print(f"Error generating employees by position chart: {e}")
    
    if user.has_perm('core.view_request'):
        try:
            requests_query = Request.objects.all()
            
            if start_date:
                requests_query = requests_query.filter(date__date__gte=start_date)
            if end_date:
                requests_query = requests_query.filter(date__date__lte=end_date)
            
            if not start_date and not end_date:
                start_date_calc = datetime.now() - timedelta(days=30)
                requests_query = requests_query.filter(date__date__gte=start_date_calc)
            
            daily_requests = requests_query.annotate(
                day=TruncDay('date')
            ).values('day').annotate(
                request_count=Count('id')
            ).order_by('day')
            
            if daily_requests:
                days = [item['day'].strftime('%Y-%m-%d') for item in daily_requests]
                counts = [item['request_count'] for item in daily_requests]
                
                charts_data.append({
                    'title': 'Количество заявок по дням',
                    'chart_id': 'daily_requests_chart',
                    'chart_type': 'line',
                    'x_data': days,
                    'y_data': counts,
                    'x_label': 'Дата',
                    'y_label': 'Количество заявок',
                    'color': 'red'
                })
        except Exception as e:
            print(f"Error generating daily requests chart: {e}")
    
    if user.has_perm('core.view_employee'):
        try:
            from datetime import date
            from django.db.models import DateField, Case, When, IntegerField
            from django.db.models.functions import ExtractYear
            
            employees_with_age = Employee.objects.annotate(
                age=ExtractYear('birthday_date') - ExtractYear(date.today())
            ).values(
                'place_of_work__name'
            ).annotate(
                avg_age=Avg('age')
            ).order_by('place_of_work__name')
            
            if employees_with_age:
                place_names = [item['place_of_work__name'] for item in employees_with_age if item['place_of_work__name']]
                avg_ages = [float(item['avg_age'] or 0) for item in employees_with_age]
                
                charts_data.append({
                    'title': 'Средний возраст сотрудников по месту работы',
                    'chart_id': 'avg_age_by_place_chart',
                    'chart_type': 'bar',
                    'x_data': place_names,
                    'y_data': avg_ages,
                    'x_label': 'Место работы',
                    'y_label': 'Средний возраст',
                    'color': 'yellow'
                })
        except Exception as e:
            print(f"Error generating avg age chart: {e}")
    
    if user.has_perm('core.view_delivery') and user.has_perm('core.view_deliveryproduct'):
        try:
            delivery_volume_by_provider = DeliveryProduct.objects.select_related('delivery', 'delivery__provider').values(
                'delivery__provider__name'
            ).annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')
            
            if delivery_volume_by_provider:
                provider_names = [item['delivery__provider__name'] for item in delivery_volume_by_provider if item['delivery__provider__name']]
                quantities = [float(item['total_quantity'] or 0) for item in delivery_volume_by_provider]
                
                charts_data.append({
                    'title': 'Объем поставок по поставщикам',
                    'chart_id': 'delivery_volume_pie_chart',
                    'chart_type': 'pie',
                    'labels': provider_names,
                    'values': quantities,
                    'color': 'pink'
                })
        except Exception as e:
            print(f"Error generating delivery volume chart: {e}")
    
    if user.has_perm('core.view_product'):
        try:
            avg_price_by_category = Product.objects.values(
                'provider__name'
            ).annotate(
                avg_price=Avg('purchase_price')
            ).order_by('-avg_price')[:10]
            
            if avg_price_by_category:
                provider_names = [item['provider__name'] for item in avg_price_by_category if item['provider__name']]
                avg_prices = [float(item['avg_price'] or 0) for item in avg_price_by_category]
                
                charts_data.append({
                    'title': 'Средняя цена продуктов по поставщикам',
                    'chart_id': 'avg_price_by_provider_chart',
                    'chart_type': 'bar',
                    'x_data': provider_names,
                    'y_data': avg_prices,
                    'x_label': 'Поставщики',
                    'y_label': 'Средняя цена (₽)',
                    'color': 'brown'
                })
        except Exception as e:
            print(f"Error generating avg price by provider chart: {e}")
    
    return charts_data

@login_required
def analytics_dashboard(request):
    """Дашборд аналитики"""
    user = request.user
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()
    
    charts_data = generate_charts_data(user, start_date, end_date)
    
    context = {
        'charts_data': charts_data,
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
    }
    
    return render(request, 'core/analytics.html', context)

class UniversalTableView(LoginRequiredMixin, ListView):
    template_name = 'core/universal_table.html'
    paginate_by = 10
    model = None
    
    def get_paginate_by(self, queryset):
        """Возвращает количество элементов на странице в зависимости от параметра per_page"""
        per_page = self.request.GET.get('per_page', 10)
        try:
            per_page = int(per_page)
            if per_page not in [10, 20, 50, 100]:
                per_page = 10
        except ValueError:
            per_page = 10
        return per_page
    
    def get_queryset(self):

        queryset = super().get_queryset()
        
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query and self.model:
            filtered_objects = []
            
            all_objects = self.model.objects.all()
            
            for obj in all_objects:
                record_string = ""
                
                for field in self.model._meta.get_fields():
                    if not hasattr(field, 'get_internal_type'):
                        continue
                    
                    field_name = field.name
                    
                    if field.many_to_many or field.auto_created:
                        continue
                    
                    try:
                        field_value = getattr(obj, field_name)
                        
                        if field_value is not None:
                            if hasattr(field_value, 'strftime'):
                                if hasattr(field_value, 'date'):
                                    field_value = field_value.strftime('%d.%m.%Y')
                                else:
                                    field_value = str(field_value)
                            
                            elif hasattr(field_value, '_meta'):
                                field_value = str(field_value)
                            
                            record_string += " " + str(field_value)
                    except:
                        continue
                
                if search_query.lower() in record_string.lower():
                    filtered_objects.append(obj)
            
            if filtered_objects:
                object_ids = [obj.id for obj in filtered_objects]
                queryset = self.model.objects.filter(id__in=object_ids)
            else:
                queryset = self.model.objects.none()
        
        order_by = self.request.GET.get('order_by', '')
        direction = self.request.GET.get('direction', 'asc')
        
        if order_by:
            try:
                field_exists = False
                for field in self.model._meta.get_fields():
                    if field.name == order_by and not field.many_to_many and not field.auto_created:
                        field_exists = True
                        break
                
                if field_exists:
                    if direction == 'desc':
                        order_by_field = f'-{order_by}'
                    else:
                        order_by_field = order_by
                    
                    queryset = queryset.order_by(order_by_field)
            except:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.model:
            context['table_title'] = self.model._meta.verbose_name_plural
            
            fields = []
            for field in self.model._meta.get_fields():
                if (not field.auto_created and 
                    field.name != 'id' and 
                    not field.many_to_many and
                    not isinstance(field, models.ManyToManyField)):
                    
                    if isinstance(field, models.ForeignKey):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'foreign_key',
                            'related_model': field.related_model,
                        })
                    elif isinstance(field, models.DateField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'date',
                        })
                    elif isinstance(field, models.ImageField) or isinstance(field, models.FileField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'image',
                        })
                    elif isinstance(field, models.DecimalField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'decimal',
                            'max_digits': field.max_digits,
                            'decimal_places': field.decimal_places,
                        })
                    elif field.choices:
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'choice',
                        })
                    else:
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'text',
                        })
            
            context['fields'] = fields
            context['model_name'] = self.model._meta.model_name
            context['search_query'] = self.request.GET.get('search', '')
            context['current_order_by'] = self.request.GET.get('order_by', '')
            context['current_direction'] = self.request.GET.get('direction', 'asc')
            
            context['has_add_permission'] = self.request.user.has_perm(f'core.add_{self.model._meta.model_name}')
            context['has_change_permission'] = self.request.user.has_perm(f'core.change_{self.model._meta.model_name}')
            context['has_delete_permission'] = self.request.user.has_perm(f'core.delete_{self.model._meta.model_name}')
        
        return context

class UniversalCreateView(LoginRequiredMixin, CreateView):
    """Универсальный View для создания записей"""
    template_name = 'core/create_form.html'
    model = None
    fields = '__all__'
    form_class = None
    
    def get_form_class(self):
        if self.model == Dish:
            from .forms import DishForm
            return DishForm
        elif self.model == Report:
            from .forms import ReportForm
            return ReportForm
        elif self.model == Request:
            from .forms import RequestForm
            return RequestForm
        elif self.model == Delivery:
            from .forms import DeliveryForm
            return DeliveryForm
        elif self.model == WorkBook:
            from .forms import WorkBookForm
            return WorkBookForm
        elif self.model == Employee:
            from .forms import EmployeeForm
            return EmployeeForm
        else:
            from .forms import UniversalForm
            class DynamicForm(UniversalForm):
                class Meta:
                    model = self.model
                    fields = '__all__'
            return DynamicForm
    
    def get_success_url(self):
        if 'action' in self.request.POST and self.request.POST['action'] == 'save_and_add':
            return self.request.path  # Остаемся на той же странице
        else:
            return reverse_lazy(f'table_{self.model._meta.model_name}')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Добавить {self.model._meta.verbose_name}'
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        context['is_create'] = True
        
        if self.model == Dish:
            all_ingredients = Ingredient.objects.all()
            selected_ingredients = []
            available_ingredients = all_ingredients
            context['selected_ingredients'] = selected_ingredients
            context['available_ingredients'] = available_ingredients
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.model == Dish:
            selected_ingredients = form.cleaned_data.get('ingredients', [])
            self.object.ingredients.set(selected_ingredients)
        
        if 'action' in self.request.POST and self.request.POST['action'] == 'save_and_add':
            return redirect(self.request.path)
        
        return response
    
    def dispatch(self, request, *args, **kwargs):
        # Проверяем права на добавление
        if not request.user.has_perm(f'core.add_{self.model._meta.model_name}'):
            messages.error(request, 'У вас нет прав для добавления записей в эту таблицу')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

class UniversalUpdateView(LoginRequiredMixin, UpdateView):
    """Универсальный View для редактирования записей"""
    template_name = 'core/create_form.html'
    model = None
    fields = '__all__'
    form_class = None
    
    def get_form_class(self):
        # Для модели Dish используем специальный Form
        if self.model == Dish:
            from .forms import DishForm
            return DishForm
        elif self.model == Report:
            from .forms import ReportForm
            return ReportForm
        elif self.model == Request:
            from .forms import RequestForm
            return RequestForm
        elif self.model == Delivery:
            from .forms import DeliveryForm
            return DeliveryForm
        elif self.model == WorkBook:
            from .forms import WorkBookForm
            return WorkBookForm
        elif self.model == Employee:
            from .forms import EmployeeForm
            return EmployeeForm
        else:
            from .forms import UniversalForm
            class DynamicForm(UniversalForm):
                class Meta:
                    model = self.model
                    fields = '__all__'
            return DynamicForm
    
    def get_success_url(self):
        return reverse_lazy(f'table_{self.model._meta.model_name}')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Изменить {self.model._meta.verbose_name}'
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        context['is_create'] = False
        
        if self.model == Dish:
            all_ingredients = Ingredient.objects.all()
            selected_ingredients = self.object.ingredients.all()
            available_ingredients = all_ingredients.exclude(
                id__in=selected_ingredients.values_list('id', flat=True)
            )
            context['selected_ingredients'] = selected_ingredients
            context['available_ingredients'] = available_ingredients
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.model == Dish:
            selected_ingredients = form.cleaned_data.get('ingredients', [])
            self.object.ingredients.set(selected_ingredients)
        
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(f'core.change_{self.model._meta.model_name}'):
            messages.error(request, 'У вас нет прав для изменения записей в этой таблице')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Переопределяем метод для передачи instance"""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        return kwargs

class UniversalDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'core/delete_confirm.html'
    model = None
    
    def get_success_url(self):
        return reverse_lazy(f'table_{self.model._meta.model_name}')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model._meta.model_name
        context['verbose_name'] = self.model._meta.verbose_name
        return context
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(f'core.delete_{self.model._meta.model_name}'):
            messages.error(request, 'У вас нет прав для удаления записей из этой таблицы')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
