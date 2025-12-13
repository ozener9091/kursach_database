from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from .models import *
from .permissions import *
from .decorators import *

@login_required
def home(request):
    return render(request, 'core/home.html', {'title': 'Главная страница'})

@login_required
def dashboard(request):
    context = {
        'title': 'Панель управления',
        'user': request.user,
        'dish_count': Dish.objects.count(),
        'employee_count': Employee.objects.count(),
        'product_count': Product.objects.count(),
        'delivery_count': Delivery.objects.count(),
        'request_count': Request.objects.count(),
        'provider_count': Provider.objects.count(),
        'report_count': Report.objects.count(),
    }
    
    return render(request, 'core/dashboard.html', context)


class TableListView(LoginRequiredMixin, ListView):
    """Базовый класс для отображения таблиц"""
    template_name = 'core/table_list.html'
    paginate_by = 20
    model = None
    table_title = ''
    fields_to_display = []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table_title'] = self.table_title
        context['fields_to_display'] = self.fields_to_display
        context['model_name'] = self.model._meta.model_name if self.model else ''
        context['has_add_permission'] = self.request.user.has_perm(f'core.add_{self.model._meta.model_name}')
        context['has_change_permission'] = self.request.user.has_perm(f'core.change_{self.model._meta.model_name}')
        context['has_delete_permission'] = self.request.user.has_perm(f'core.delete_{self.model._meta.model_name}')
        return context
    
    def get_queryset(self):
        # Базовый queryset - все объекты
        return self.model.objects.all()


@login_required
def director_tables(request):
    """Список всех таблиц для директора"""
    if not request.user.groups.filter(name='Директор').exists() and not request.user.is_superuser:
        from django.contrib import messages
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('dashboard')
    
    from django.apps import apps
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
            from django.contrib import messages
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('dashboard')
    
    # Таблицы для менеджера
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
        # Проверяем, может пользователь директор?
        if not request.user.groups.filter(name='Директор').exists():
            from django.contrib import messages
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
        # Проверяем, может пользователь директор?
        if not request.user.groups.filter(name='Директор').exists():
            from django.contrib import messages
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


class UniversalTableView(LoginRequiredMixin, ListView):
    """Универсальный View для отображения всех таблиц"""
    template_name = 'core/universal_table.html'
    paginate_by = 20
    model = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Получаем поисковый запрос
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query and self.model:
            # Получаем все текстовые поля модели
            text_fields = []
            for field in self.model._meta.get_fields():
                # Ищем текстовые поля (CharField, TextField)
                if (hasattr(field, 'get_internal_type') and 
                    field.get_internal_type() in ['CharField', 'TextField', 'EmailField', 'URLField']):
                    text_fields.append(field.name)
            
            # Также ищем в ForeignKey полях (через связанные объекты)
            fk_fields = []
            for field in self.model._meta.get_fields():
                if (hasattr(field, 'get_internal_type') and 
                    field.get_internal_type() == 'ForeignKey'):
                    fk_fields.append(field.name)
            
            # Создаем Q-объекты для поиска
            q_objects = Q()
            
            # Поиск по текстовым полям
            for field_name in text_fields:
                q_objects |= Q(**{f'{field_name}__icontains': search_query})
            
            # Поиск по ForeignKey полям (через связанные объекты)
            for fk_field in fk_fields:
                # Пробуем поиск по полю name в связанном объекте
                q_objects |= Q(**{f'{fk_field}__name__icontains': search_query})
                # Также пробуем другие возможные текстовые поля
                q_objects |= Q(**{f'{fk_field}__title__icontains': search_query})
            
            # Если есть условия для поиска
            if q_objects:
                queryset = queryset.filter(q_objects).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.model:
            # Получаем название таблицы
            context['table_title'] = self.model._meta.verbose_name_plural
            
            # Получаем все поля модели, кроме id и полей ManyToMany
            fields = []
            for field in self.model._meta.get_fields():
                # Исключаем:
                # 1. Поля ManyToMany (они отображаются через related_name)
                # 2. Поле id (автоинкремент)
                # 3. Обратные связи
                if (not field.auto_created and 
                    field.name != 'id' and 
                    not field.many_to_many and
                    not isinstance(field, models.ManyToManyField)):
                    
                    # Для ForeignKey получаем связанный объект
                    if isinstance(field, models.ForeignKey):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'foreign_key',
                            'related_model': field.related_model,
                        })
                    # Для DateTimeField
                    elif isinstance(field, models.DateTimeField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'datetime',
                        })
                    # Для DateField
                    elif isinstance(field, models.DateField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'date',
                        })
                    # Для BooleanField
                    elif isinstance(field, models.BooleanField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'boolean',
                        })
                    # Для ImageField/FileField
                    elif isinstance(field, models.ImageField) or isinstance(field, models.FileField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'image',
                        })
                    # Для DecimalField
                    elif isinstance(field, models.DecimalField):
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'decimal',
                            'max_digits': field.max_digits,
                            'decimal_places': field.decimal_places,
                        })
                    # Для ChoiceField
                    elif field.choices:
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'choice',
                        })
                    # Для остальных полей (CharField, TextField и т.д.)
                    else:
                        fields.append({
                            'name': field.name,
                            'verbose_name': field.verbose_name,
                            'type': 'text',
                        })
            
            context['fields'] = fields
            context['model_name'] = self.model._meta.model_name
            context['search_query'] = self.request.GET.get('search', '')
            
            # Проверяем права доступа
            context['has_add_permission'] = self.request.user.has_perm(f'core.add_{self.model._meta.model_name}')
            context['has_change_permission'] = self.request.user.has_perm(f'core.change_{self.model._meta.model_name}')
            context['has_delete_permission'] = self.request.user.has_perm(f'core.delete_{self.model._meta.model_name}')
        
        return context
