from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

class RoleRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки роли пользователя"""
    role_name = None
    permission_required = None
    login_url = reverse_lazy('login')
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        if self.role_name:
            return user.groups.filter(name=self.role_name).exists()
        
        if self.permission_required:
            if isinstance(self.permission_required, str):
                return user.has_perm(self.permission_required)
            return all(user.has_perm(perm) for perm in self.permission_required)
        
        return True
    
    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет доступа к этой странице.')
        return redirect(self.login_url)


class DirectorRequiredMixin(RoleRequiredMixin):
    role_name = 'Директор'

class ManagerRequiredMixin(RoleRequiredMixin):
    role_name = 'Менеджер'

class ChefRequiredMixin(RoleRequiredMixin):
    role_name = 'Шеф-повар'

class HRManagerRequiredMixin(RoleRequiredMixin):
    role_name = 'Менеджер по кадрам'


class ViewPermissionMixin(PermissionRequiredMixin):
    def get_permission_required(self):
        model_name = self.model._meta.model_name
        return [f'core.view_{model_name}']

class AddPermissionMixin(PermissionRequiredMixin):
    def get_permission_required(self):
        model_name = self.model._meta.model_name
        return [f'core.add_{model_name}']

class ChangePermissionMixin(PermissionRequiredMixin):
    def get_permission_required(self):
        model_name = self.model._meta.model_name
        return [f'core.change_{model_name}']

class DeletePermissionMixin(PermissionRequiredMixin):
    def get_permission_required(self):
        model_name = self.model._meta.model_name
        return [f'core.delete_{model_name}']