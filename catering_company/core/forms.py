from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ModelMultipleChoiceField
from .models import *
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш email'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email не найден')
        return email

class DishForm(ModelForm):
    ingredients = ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Ингредиенты'
    )
    
    class Meta:
        model = Dish
        fields = '__all__'
        exclude = ['ingredients']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'output': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'assortment_group': forms.Select(attrs={'class': 'form-select'}),
            'unit_of_measurement': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['ingredients'].initial = self.instance.ingredients.all()

class RequestForm(ModelForm):
    class Meta:
        model = Request
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-select'}),
        }

class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-select'}),
        }

class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'}),
        }

class WorkBookForm(ModelForm):
    class Meta:
        model = WorkBook
        fields = '__all__'
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'}),
            'reason_for_dismissal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'place_of_work': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'profession': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'classification': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday_date': forms.DateInput(attrs={'type': 'date-local', 'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'work_experience': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'street': forms.Select(attrs={'class': 'form-select'}),
        }

class UniversalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field, ModelMultipleChoiceField):
                if isinstance(field, forms.DateField):
                    field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                elif isinstance(field, forms.TimeField):
                    field.widget = forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})
                    if isinstance(field, forms.DecimalField) or isinstance(field, forms.FloatField):
                        field.widget.attrs.update({'step': 'any'})
                    elif isinstance(field, forms.IntegerField):
                        field.widget.attrs.update({'step': '1'})