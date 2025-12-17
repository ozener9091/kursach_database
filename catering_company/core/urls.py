from django.urls import path
from django.contrib.auth import views as auth_views
from django.apps import apps
from . import views

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
    path('password-reset/', views.password_reset_request, name='password_reset'),

    path('tables/director/', views.director_tables, name='director_tables'),
    path('tables/manager/', views.manager_tables, name='manager_tables'),
    path('tables/chef/', views.chef_tables, name='chef_tables'),
    path('tables/hr/', views.hr_tables, name='hr_tables'),
    path('sql-query/', views.sql_query_page, name='sql_query'),
    path('help/', views.help_page, name='help'),
    path('help/manual/', views.user_manual, name='user_manual'),
    path('help/about/', views.about_app, name='about_app'),
    path('miscellaneous/', views.miscellaneous_page, name='miscellaneous'),
    path('settings/', views.settings_page, name='settings'),
    path('update-theme/', views.update_theme, name='update_theme'),
    path('change-password/', views.change_password, name='change_password'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
]

for model in app_models:
    model_name = model._meta.model_name
    
    if model_name in ['abbreviationtype', 'gendertype', 'eventtype']:
        continue
    
    view_class = type(
        f'{model_name.title()}UniversalView',
        (views.UniversalTableView,),
        {'model': model}
    )
    
    create_view_class = type(
        f'{model_name.title()}CreateView',
        (views.UniversalCreateView,),
        {'model': model}
    )
    
    update_view_class = type(
        f'{model_name.title()}UpdateView',
        (views.UniversalUpdateView,),
        {'model': model}
    )
    
    delete_view_class = type(
        f'{model_name.title()}DeleteView',
        (views.UniversalDeleteView,),
        {'model': model}
    )
    
    urlpatterns.extend([
        path(f'table/{model_name}/', view_class.as_view(), name=f'table_{model_name}'),
        path(f'table/{model_name}/add/', create_view_class.as_view(), name=f'add_{model_name}'),
        path(f'table/{model_name}/edit/<int:pk>/', update_view_class.as_view(), name=f'edit_{model_name}'),
        path(f'table/{model_name}/delete/<int:pk>/', delete_view_class.as_view(), name=f'delete_{model_name}'),
    ])
