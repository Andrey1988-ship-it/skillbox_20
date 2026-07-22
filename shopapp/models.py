from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Product(models.Model):
    """Модель товара (брелок)"""
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    discount = models.PositiveSmallIntegerField(default=0, verbose_name='Скидка (%)')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_archived = models.BooleanField(default=False, verbose_name="Архивирован")
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.price} ₽"

    def get_absolute_url(self):
        return reverse('shopapp:product_detail', args=[self.slug or self.id])


class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('paid', 'Оплачен'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь',
                             null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес доставки')
    comment = models.TextField(verbose_name='Комментарий к заказу', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.first_name} {self.last_name}"

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_cost(self):
        """Получить стоимость с защитой от None"""
        # Защита от None значений
        price = self.price if self.price is not None else 0
        quantity = self.quantity if self.quantity is not None else 0

        # Приводим к Decimal для точного умножения
        from decimal import Decimal
        return Decimal(str(price)) * Decimal(str(quantity))


# shopapp/models.py - исправленная модель UploadedFile

class UploadedFile(models.Model):
    """Модель для хранения загруженных файлов"""
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name='Файл'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    file_size = models.PositiveIntegerField(
        editable=False,
        verbose_name='Размер файла (байт)'
    )
    content_type = models.CharField(
        max_length=100,
        blank=True,  # Разрешаем пустое значение
        editable=False,
        verbose_name='Тип файла'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Загрузил'
    )

    class Meta:
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file.name} ({self.file_size} байт)"

    def save(self, *args, **kwargs):
        # Сохраняем размер файла
        if self.file:
            self.file_size = self.file.size
            # Пытаемся получить content_type, если есть
            if hasattr(self.file, 'content_type'):
                self.content_type = self.file.content_type
            elif hasattr(self.file.file, 'content_type'):
                self.content_type = self.file.file.content_type
        super().save(*args, **kwargs)