# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
    
    # Ролевые страницы с таблицами
    path('tables/director/', views.director_tables, name='director_tables'),
    path('tables/manager/', views.manager_tables, name='manager_tables'),
    path('tables/chef/', views.chef_tables, name='chef_tables'),
    path('tables/hr/', views.hr_tables, name='hr_tables'),
    
    # Конкретные таблицы
    path('table/dish/', views.DishListView.as_view(), name='table_dish'),
    path('table/ingredient/', views.IngredientListView.as_view(), name='table_ingredient'),
    path('table/product/', views.ProductListView.as_view(), name='table_product'),
    path('table/provider/', views.ProviderListView.as_view(), name='table_provider'),
    path('table/employee/', views.EmployeeListView.as_view(), name='table_employee'),
    path('table/delivery/', views.DeliveryListView.as_view(), name='table_delivery'),
    path('table/request/', views.RequestListView.as_view(), name='table_request'),
    path('table/report/', views.ReportListView.as_view(), name='table_report'),
    path('table/position/', views.PositionListView.as_view(), name='table_position'),
    path('table/workbook/', views.WorkBookListView.as_view(), name='table_workbook'),
    
    # Справочники
    path('table/country/', views.CountryListView.as_view(), name='table_country'),
    path('table/city/', views.CityListView.as_view(), name='table_city'),
    path('table/street/', views.StreetListView.as_view(), name='table_street'),
    path('table/unitofmeasurement/', views.UnitOfMeasurementListView.as_view(), name='table_unitofmeasurement'),
    path('table/assortmentgroup/', views.AssortmentGroupListView.as_view(), name='table_assortmentgroup'),
    path('table/bank/', views.BankListView.as_view(), name='table_bank'),

    path('table/reportdish/', views.ReportDishListView.as_view(), name='table_reportdish'),
    path('table/requestproduct/', views.RequestProductListView.as_view(), name='table_requestproduct'),
    path('table/deliveryproduct/', views.DeliveryProductListView.as_view(), name='table_deliveryproduct'),
    path('table/placeofwork/', views.PlaceOfWorkListView.as_view(), name='table_placeofwork'),
    path('table/department/', views.DepartmentListView.as_view(), name='table_department'),
    path('table/profession/', views.ProfessionListView.as_view(), name='table_profession'),
    path('table/specialization/', views.SpecializationListView.as_view(), name='table_specialization'),
    path('table/classification/', views.ClassificationListView.as_view(), name='table_classification'),
    path('table/division/', views.DivisionListView.as_view(), name='table_division'),
    
]