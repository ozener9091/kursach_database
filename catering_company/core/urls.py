from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from django.apps import apps
from .views import UniversalTableView

app_models = apps.get_app_config('core').get_models()

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='core/logout.html'
    ), name='logout'),
    
    path('tables/director/', views.director_tables, name='director_tables'),
    path('tables/manager/', views.manager_tables, name='manager_tables'),
    path('tables/chef/', views.chef_tables, name='chef_tables'),
    path('tables/hr/', views.hr_tables, name='hr_tables'),
    
]

for model in app_models:
    model_name = model._meta.model_name
    
    if model_name in ['abbreviationtype', 'gendertype', 'eventtype']:
        continue
    
    view_class = type(
        f'{model_name.title()}UniversalView',
        (UniversalTableView,),
        {'model': model}
    )
    
    # Добавляем URL pattern
    urlpatterns.append(
        path(f'table/{model_name}/', view_class.as_view(), name=f'table_{model_name}')
    )

