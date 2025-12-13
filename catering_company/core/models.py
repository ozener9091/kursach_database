from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
User = get_user_model()


class AbbreviationType(models.TextChoices):
    OOO = "ООО"
    AO = "АО"
    IP = "ИП"
    PAO = "ПАО"
    PK = "ПК"
    KPKG = "КПКГ"
    GUP = "ГУП"
    MUP = "МУП"
    FKP = "ФКП"
    NKO = "НКО"


class GenderType(models.TextChoices):

    MALE = "Мужской"
    FEMALE = "Женский"


class EventType(models.TextChoices):

    HIRING = "Прием"
    DISMISSAL = "Увольнение"
    TRANSFER = "Перевод"


class AssortmentGroup(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Группа ассортимента'
    )

    class Meta:
        verbose_name = 'группа ассортимента'
        verbose_name_plural = 'Группы ассортимента'
        ordering = ['-name']

    def __str__(self):
        return self.name


class UnitOfMeasurement(models.Model):

    name = models.CharField(
        max_length=8,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    gross_weight = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='Вес брутто'
    )

    net_weight = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='Вес нетто'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Dish(models.Model):

    name = models.CharField(
        max_length=30,
        null=False,
        verbose_name='Название'
    )

    price = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена'
    )

    output = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='Выход'
    )

    description = models.TextField(
        null=False,
        verbose_name='Краткое описание приготовления'
    )

    image = models.ImageField(
        null=True,
        upload_to='dishes/',
        verbose_name='Фото'
        )

    assortment_group = models.ForeignKey(
        'AssortmentGroup',
        on_delete=models.CASCADE,
        null=False,
        verbose_name='Группа ассортимента'
    )

    unit_of_measurement = models.ForeignKey(
        'UnitOfMeasurement',
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Единицы измерения'
    )

    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты'
    )

    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Bank(models.Model):

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Название'
    )

    correspondent_account_number = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Номер корреспондентского счёта'
    )

    bank_identification_code = models.CharField(
        max_length=9,
        null=False,
        verbose_name='БИК'
    )

    taxpayer_identification_number = models.CharField(
        max_length=10,
        null=False,
        verbose_name='ИНН'
    )

    class Meta:
        verbose_name = 'банк'
        verbose_name_plural = 'Банки'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Country(models.Model):

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'страна'
        verbose_name_plural = 'Страны'
        ordering = ['-name']

    def __str__(self):
        return self.name


class City(models.Model):

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'город'
        verbose_name_plural = 'Города'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Street(models.Model):

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'улица'
        verbose_name_plural = 'Улицы'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Provider(models.Model):

    name = models.CharField(
        max_length=30,
        null=False,
        verbose_name='Название'
    )

    code = models.CharField(
        max_length=8,
        null=False,
        verbose_name='Код по ОК'
    )

    abbreviation = models.CharField(
        max_length=20,
        choices=AbbreviationType.choices
    )

    account_number = models.CharField(
        max_length=30,
        null=False,
        verbose_name='Номер расчётного счёта'
    )

    director_first_name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Имя руководителя'
    )

    director_last_name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Фамилия руководителя'
    )

    director_phone = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Номер телефона руководителя'
    )

    house_number = models.CharField(
        max_length=6,
        null=False,
        verbose_name='Номер дома'
    )

    bank = models.ForeignKey(
        'Bank',
        on_delete=models.CASCADE,
        verbose_name='Банк')

    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        verbose_name='Страна')

    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        verbose_name='Город')

    street = models.ForeignKey(
        'Street',
        on_delete=models.CASCADE,
        verbose_name='Улица')

    class Meta:
        verbose_name = 'поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(
        max_length=40,
        null=False,
        verbose_name='Название'
    )

    price_premium = models.DecimalField(
        null=False,
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0),],
        verbose_name='Ценовая надбавка (в %)'
    )

    remaining_stock = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0),],
        verbose_name='Остаток на складе'
    )

    purchase_price = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0),],
        verbose_name='Закупочная цена'
    )

    unit_of_measurement = models.ForeignKey(
        'UnitOfMeasurement',
        on_delete=models.CASCADE,
        verbose_name='Единицы измерения'
    )

    provider = models.ForeignKey(
        'Provider',
        on_delete=models.CASCADE,
        verbose_name='Поставщик')

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Delivery(models.Model):

    date = models.DateTimeField(
        null=False,
        verbose_name='Дата поставки',
    )

    provider = models.ForeignKey(
        'Provider',
        on_delete=models.CASCADE,
        verbose_name='Поставщик'
    )

    class Meta:
        verbose_name = 'поставка'
        verbose_name_plural = 'Поставки'
        ordering = ['-date']

    def __str__(self):
        return self.date.strftime('%d.%m.%Y %H:%M')


class DeliveryProduct(models.Model):

    delivery = models.ForeignKey(
        'Delivery',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
    )

    quantity = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0),],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'продукт в поставке'
        verbose_name_plural = 'Продукты в поставке'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Division(models.Model):

    name = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'подразделение предприятия'
        verbose_name_plural = 'Подразделения предприятия'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Request(models.Model):

    date = models.DateTimeField(
        null=False,
        verbose_name='Дата заявки',
    )

    division = models.ForeignKey(
        'Division',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-date']

    def __str__(self):
        return self.date.strftime('%d.%m.%Y %H:%M')


class RequestProduct(models.Model):

    request = models.ForeignKey(
        'Request',
        on_delete=models.CASCADE,
        verbose_name='Заявка'
    )

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )

    quantity = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0),],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'продукт в заявке'
        verbose_name_plural = 'Продукты в заявке'

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Report(models.Model):

    date = models.DateTimeField(
        null=False,
        verbose_name='Дата отчёта по реализации',
    )

    class Meta:
        verbose_name = 'отчёт по реализации'
        verbose_name_plural = 'Отчёты по реализации'
        ordering = ['-date']

    def __str__(self):
        return self.date.strftime('%d.%m.%Y %H:%M')


class ReportDish(models.Model):

    report = models.ForeignKey(
        'Report',
        on_delete=models.CASCADE,
        verbose_name='Отчёт по реализации'
    )

    dish = models.ForeignKey(
        'Dish',
        on_delete=models.CASCADE,
        verbose_name='Блюдо'
    )

    quantity = models.DecimalField(
        null=False,
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0),],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'блюдо в отчёте'
        verbose_name_plural = 'Блюда в отчёте'

    def __str__(self):
        return f"{self.dish.name} - {self.quantity}"


class Position(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    code = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Код по ОКПДТР'
    )

    class Meta:
        verbose_name = 'должность'
        verbose_name_plural = 'Должности'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Employee(models.Model):

    first_name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Фамилия'
    )

    middle_name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Отчество'
    )

    birthday_date = models.DateTimeField(
        null=False,
        verbose_name='День рождения',
    )

    house_number = models.CharField(
        max_length=6,
        null=False,
        verbose_name='Номер дома'
    )

    work_experience = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Трудовой стаж'
    )

    gender = models.CharField(
        max_length=20,
        choices=GenderType.choices
    )

    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        verbose_name='Должность'
    )

    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        verbose_name='Страна'
    )

    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        verbose_name='Город'
    )

    street = models.ForeignKey(
        'Street',
        on_delete=models.CASCADE,
        verbose_name='Улица'
    )

    class Meta:
        verbose_name = 'работник'
        verbose_name_plural = 'Работники'
        ordering = ['-last_name']

    def __str__(self):
        return self.last_name


class PlaceOfWork(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        verbose_name='Страна'
    )

    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        verbose_name='Город'
    )

    street = models.ForeignKey(
        'Street',
        on_delete=models.CASCADE,
        verbose_name='Улица'
    )

    class Meta:
        verbose_name = 'место работы'
        verbose_name_plural = 'Места работы'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Department(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'структурное подразделение'
        verbose_name_plural = 'Структурные подразделения'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Profession(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'профессия'
        verbose_name_plural = 'Профессии'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Specialization(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'специализация'
        verbose_name_plural = 'Специализации'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Classification(models.Model):

    name = models.CharField(
        max_length=25,
        null=False,
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'классификация'
        verbose_name_plural = 'Классификации'
        ordering = ['-name']

    def __str__(self):
        return self.name


class WorkBook(models.Model):

    event_date = models.DateTimeField(
        null=True,
        verbose_name='Дата записи',
    )

    reason_for_dismissal = models.TextField(
        null=True,
        verbose_name='Причина прекращения ТД'
    )

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices
    )

    number = models.CharField(
        max_length=20,
        null=False,
        verbose_name='Номер'
    )

    document_type = models.CharField(
        max_length=30,
        null=False,
        verbose_name='Тип документа'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Работник')

    place_of_work = models.ForeignKey(
        PlaceOfWork,
        on_delete=models.CASCADE,
        verbose_name='Место работы')

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name='Структурное подразделение')

    profession = models.ForeignKey(
        Profession,
        on_delete=models.CASCADE,
        verbose_name='Профессия')

    specialization = models.ForeignKey(
        Specialization,
        on_delete=models.CASCADE,
        verbose_name='Специализация')

    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        verbose_name='Классификация')

    class Meta:
        verbose_name = 'запись в трудовой книге'
        verbose_name_plural = 'Записи в трудовой книге'
        ordering = ['-event_date']

    def __str__(self):
        if self.event_date:
            return f"{self.employee.last_name} - {self.event_date.strftime('%d.%m.%Y')}"
        return f"{self.employee.last_name} - запись"

