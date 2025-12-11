# core/management/commands/create_test_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Создает тестовых пользователей для каждой роли'

    def handle(self, *args, **kwargs):
        # Пароль для всех тестовых пользователей
        password = 'test123'
        
        users_data = [
            {'username': 'director', 'email': 'director@example.com', 'group': 'Директор'},
            {'username': 'manager', 'email': 'manager@example.com', 'group': 'Менеджер'},
            {'username': 'chef', 'email': 'chef@example.com', 'group': 'Шеф-повар'},
            {'username': 'hr_manager', 'email': 'hr@example.com', 'group': 'Менеджер по кадрам'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'email': user_data['email']}
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.username}'))
            
            # Назначаем группу
            group = Group.objects.get(name=user_data['group'])
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f'Назначена роль {user_data["group"]} для {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('Все тестовые пользователи созданы!'))
        self.stdout.write(self.style.WARNING(f'Пароль для всех пользователей: {password}'))