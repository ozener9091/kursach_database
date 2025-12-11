# core/management/commands/create_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = 'Создает стандартные роли и назначает им права'

    def handle(self, *args, **kwargs):
        # Определяем модели для каждой роли
        models_config = {
            'director': {
                'full_access': [
                    'assortmentgroup', 'unitofmeasurement', 'ingredient', 'dish',
                    'bank', 'country', 'city', 'street', 'provider', 'product',
                    'delivery', 'deliveryproduct', 'division', 'request', 'requestproduct',
                    'report', 'reportdish', 'position', 'employee', 'placeofwork',
                    'department', 'profession', 'specialization', 'classification', 'workbook'
                ]
            },
            'manager': {
                'view': [
                    'assortmentgroup', 'unitofmeasurement', 'ingredient', 'dish',
                    'bank', 'country', 'city', 'street', 'provider', 'product',
                    'delivery', 'deliveryproduct', 'division', 'request', 'requestproduct',
                    'report', 'reportdish'
                ],
                'add_change_delete': [
                    'dish', 'ingredient', 'request', 'requestproduct',
                    'delivery', 'deliveryproduct'
                ]
            },
            'chef': {
                'view': [
                    'dish', 'product', 'assortmentgroup', 'unitofmeasurement',
                    'ingredient', 'country', 'city', 'street'
                ],
                'change': ['ingredient']
            },
            'hr_manager': {
                'view': [
                    'position', 'employee', 'placeofwork', 'department',
                    'profession', 'specialization', 'classification', 'workbook',
                    'country', 'city', 'street'
                ],
                'add_change_delete': [
                    'position', 'employee', 'placeofwork', 'department',
                    'profession', 'specialization', 'classification', 'workbook'
                ]
            }
        }

        # Справочники (доступны всем ролям для просмотра)
        reference_models = ['country', 'city', 'street', 'unitofmeasurement', 'assortmentgroup']

        # Создаем группы
        groups = {
            'Директор': Group.objects.get_or_create(name='Директор')[0],
            'Менеджер': Group.objects.get_or_create(name='Менеджер')[0],
            'Шеф-повар': Group.objects.get_or_create(name='Шеф-повар')[0],
            'Менеджер по кадрам': Group.objects.get_or_create(name='Менеджер по кадрам')[0],
        }

        # Функция для получения permission кодов
        def get_permission_codename(action, model_name):
            model = apps.get_model('core', model_name)
            content_type = ContentType.objects.get_for_model(model)
            
            if action == 'view':
                # Для view используем стандартное permission
                return f'view_{model_name}'
            elif action == 'add':
                return f'add_{model_name}'
            elif action == 'change':
                return f'change_{model_name}'
            elif action == 'delete':
                return f'delete_{model_name}'
            return None

        # Назначаем права для каждой роли
        for role_name, config in models_config.items():
            group = groups[{
                'director': 'Директор',
                'manager': 'Менеджер',
                'chef': 'Шеф-повар',
                'hr_manager': 'Менеджер по кадрам'
            }[role_name]]
            
            # Очищаем текущие права
            group.permissions.clear()
            
            permissions_to_add = []
            
            # Директор - полный доступ ко всему
            if role_name == 'director':
                for model_name in config['full_access']:
                    for action in ['view', 'add', 'change', 'delete']:
                        try:
                            perm_codename = get_permission_codename(action, model_name)
                            if perm_codename:
                                perm = Permission.objects.get(codename=perm_codename)
                                permissions_to_add.append(perm)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Permission не найден: {perm_codename}'))
            
            # Менеджер
            elif role_name == 'manager':
                # Просмотр всех указанных моделей
                for model_name in config['view']:
                    try:
                        perm = Permission.objects.get(codename=get_permission_codename('view', model_name))
                        permissions_to_add.append(perm)
                    except:
                        pass
                
                # Добавление/изменение/удаление для specific моделей
                for model_name in config['add_change_delete']:
                    for action in ['add', 'change', 'delete']:
                        try:
                            perm = Permission.objects.get(codename=get_permission_codename(action, model_name))
                            permissions_to_add.append(perm)
                        except:
                            pass
            
            # Шеф-повар
            elif role_name == 'chef':
                # Просмотр
                for model_name in config['view']:
                    try:
                        perm = Permission.objects.get(codename=get_permission_codename('view', model_name))
                        permissions_to_add.append(perm)
                    except:
                        pass
                
                # Изменение ингредиентов
                for model_name in config['change']:
                    try:
                        perm = Permission.objects.get(codename=get_permission_codename('change', model_name))
                        permissions_to_add.append(perm)
                    except:
                        pass
            
            # Менеджер по кадрам
            elif role_name == 'hr_manager':
                # Просмотр
                for model_name in config['view']:
                    try:
                        perm = Permission.objects.get(codename=get_permission_codename('view', model_name))
                        permissions_to_add.append(perm)
                    except:
                        pass
                
                # Добавление/изменение/удаление
                for model_name in config['add_change_delete']:
                    for action in ['add', 'change', 'delete']:
                        try:
                            perm = Permission.objects.get(codename=get_permission_codename(action, model_name))
                            permissions_to_add.append(perm)
                        except:
                            pass
            
            # Добавляем права на просмотр справочников всем ролям
            for model_name in reference_models:
                try:
                    perm = Permission.objects.get(codename=get_permission_codename('view', model_name))
                    if perm not in permissions_to_add:
                        permissions_to_add.append(perm)
                except:
                    pass
            
            # Применяем права к группе
            group.permissions.set(permissions_to_add)
            self.stdout.write(self.style.SUCCESS(f'Создана группа: {group.name} с {len(permissions_to_add)} правами'))

        self.stdout.write(self.style.SUCCESS('Все роли успешно созданы!'))