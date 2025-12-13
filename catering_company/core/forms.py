from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ModelMultipleChoiceField
from .models import Dish, Ingredient
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

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
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'output': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если форма создается для редактирования существующего объекта
        if self.instance and self.instance.pk:
            self.fields['ingredients'].initial = self.instance.ingredients.all()

class UniversalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем Bootstrap классы ко всем полям
        for field_name, field in self.fields.items():
            if not isinstance(field, ModelMultipleChoiceField):
                field.widget.attrs.update({'class': 'form-control'})
                # Для числовых полей устанавливаем шаг
                if isinstance(field, forms.DecimalField) or isinstance(field, forms.FloatField):
                    field.widget.attrs.update({'step': 'any'})
                elif isinstance(field, forms.IntegerField):
                    field.widget.attrs.update({'step': '1'})

