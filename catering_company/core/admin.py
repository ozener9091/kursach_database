from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from .models import (
    AssortmentGroup, UnitOfMeasurement, Ingredient, Dish,
    Bank, Country, City, Street, Provider, Product,
    Delivery, DeliveryProduct, Division, Request, RequestProduct,
    Report, ReportDish, Position, Employee, PlaceOfWork,
    Department, Profession, Specialization, Classification, WorkBook
)

User = get_user_model()

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permissions_count')
    filter_horizontal = ('permissions',)
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    get_permissions_count.short_description = 'Количество прав'

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(AssortmentGroup)
class AssortmentGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(UnitOfMeasurement)
class UnitOfMeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gross_weight', 'net_weight')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'output', 'assortment_group', 'unit_of_measurement')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_filter = ('assortment_group', 'unit_of_measurement')
    filter_horizontal = ('ingredients',)
    ordering = ('name',)
    readonly_fields = ('display_ingredients',)
    
    def display_ingredients(self, obj):
        return ", ".join([ingredient.name for ingredient in obj.ingredients.all()])
    display_ingredients.short_description = 'Ингредиенты'

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'bank_identification_code', 'taxpayer_identification_number')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'bank_identification_code')
    ordering = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbreviation', 'director_last_name', 'city', 'bank')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'director_last_name', 'director_first_name')
    list_filter = ('abbreviation', 'city', 'bank')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'purchase_price', 'price_premium', 'remaining_stock', 'provider', 'unit_of_measurement')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('provider', 'unit_of_measurement')
    ordering = ('name',)

class DeliveryProductInline(admin.TabularInline):
    model = DeliveryProduct
    extra = 1
    fields = ('product', 'quantity')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'provider')
    list_display_links = ('id', 'date')
    search_fields = ('provider__name',)
    list_filter = ('date', 'provider')
    ordering = ('-date',)
    inlines = [DeliveryProductInline]

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

class RequestProductInline(admin.TabularInline):
    model = RequestProduct
    extra = 1
    fields = ('product', 'quantity')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'division')
    list_display_links = ('id', 'date')
    search_fields = ('division__name',)
    list_filter = ('date', 'division')
    ordering = ('-date',)
    inlines = [RequestProductInline]

class ReportDishInline(admin.TabularInline):
    model = ReportDish
    extra = 1
    fields = ('dish', 'quantity')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'date')
    list_display_links = ('id', 'date')
    search_fields = ('date',)
    list_filter = ('date',)
    ordering = ('-date',)
    inlines = [ReportDishInline]

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'middle_name', 'position', 'gender', 'birthday_date')
    list_display_links = ('id', 'last_name')
    search_fields = ('last_name', 'first_name', 'middle_name')
    list_filter = ('position', 'gender', 'city', 'country')
    ordering = ('last_name', 'first_name')

@admin.register(PlaceOfWork)
class PlaceOfWorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'city', 'street')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('country', 'city')
    ordering = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(WorkBook)
class WorkBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'event_date', 'event_type', 'place_of_work', 'profession')
    list_display_links = ('id', 'employee')
    search_fields = ('employee__last_name', 'employee__first_name', 'place_of_work__name')
    list_filter = ('event_type', 'event_date', 'profession', 'department')
    ordering = ('-event_date',)
    
@admin.register(DeliveryProduct)
class DeliveryProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery', 'product', 'quantity')
    list_display_links = ('id', 'delivery')
    search_fields = ('product__name', 'delivery__provider__name')
    list_filter = ('product',)

@admin.register(RequestProduct)
class RequestProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'product', 'quantity')
    list_display_links = ('id', 'request')
    search_fields = ('product__name', 'request__division__name')
    list_filter = ('product',)

@admin.register(ReportDish)
class ReportDishAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'dish', 'quantity')
    list_display_links = ('id', 'report')
    search_fields = ('dish__name',)
    list_filter = ('dish',)