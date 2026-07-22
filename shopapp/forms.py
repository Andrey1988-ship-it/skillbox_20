from .models import Order, Product, OrderItem
from django import forms
from django.core.exceptions import ValidationError


class OrderCreateForm(forms.ModelForm):
    """Форма для создания заказа пользователем"""

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Город, улица, дом, квартира'}),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Пожелания по доставке...'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Телефон',
            'address': 'Адрес доставки',
            'comment': 'Комментарий к заказу',
        }

    def clean_phone(self):
        """Проверка телефона"""
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError('Введите корректный номер телефона')
        return phone


class AdminOrderCreateForm(forms.ModelForm):
    """Форма для создания заказа с товарами"""

    # Поле для выбора товаров
    items = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(is_active=True, stock__gt=0),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5}),
        required=True,
        label='Товары (выберите один или несколько)'
    )

    class Meta:
        model = Order
        fields = ['user', 'first_name', 'last_name', 'email', 'phone', 'address', 'comment', 'status', 'items']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        order = super().save(commit=commit)

        if commit:
            # Добавляем выбранные товары в заказ
            products = self.cleaned_data.get('items')
            for product in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=1  # можно добавить поле для количества
                )

        return order



class FileUploadForm(forms.Form):
    """Форма для загрузки файлов с проверкой размера"""
    file = forms.FileField(
        label='Выберите файл',
        help_text='Максимальный размер файла: 1 МБ'
    )
    description = forms.CharField(
        max_length=255,
        required=False,
        label='Описание файла',
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def clean_file(self):
        file = self.cleaned_data['file']

        # Проверка размера файла (1 МБ = 1048576 байт)
        max_size = 1 * 1024 * 1024  # 1 МБ

        if file.size > max_size:
            raise ValidationError(
                f'Файл слишком большой! Максимальный размер: 1 МБ. '
                f'Ваш файл: {file.size / (1024 * 1024):.2f} МБ'
            )

        # Дополнительная проверка на тип файла (опционально)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']
        if file.content_type not in allowed_types:
            raise ValidationError(
                f'Неподдерживаемый тип файла. Разрешены: {", ".join(allowed_types)}'
            )

        return file


class ProductCreateForm(forms.ModelForm):
    """Форма для создания продукта"""

    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'discount', 'stock', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'url-slug'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Описание товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'discount': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Название',
            'slug': 'URL (уникальный идентификатор)',
            'description': 'Описание',
            'price': 'Цена (руб.)',
            'discount': 'Скидка (%)',
            'stock': 'Количество на складе',
            'is_active': 'Активен',
        }
        help_texts = {
            'slug': 'Только латиница, цифры и дефисы. Например: "brelok-1"',
            'price': 'Цена в рублях',
            'discount': 'Процент скидки (0-100)',
        }

    def clean_slug(self):
        """Проверка уникальности slug"""
        slug = self.cleaned_data.get('slug')
        if slug:
            # Заменяем пробелы на дефисы
            slug = slug.lower().replace(' ', '-')
            # Проверяем существование
            if Product.objects.filter(slug=slug).exists():
                raise forms.ValidationError(f'Товар с таким slug "{slug}" уже существует')
        return slug

    def clean_price(self):
        """Проверка цены"""
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        return price

    def clean_stock(self):
        """Проверка количества"""
        stock = self.cleaned_data.get('stock')
        if stock and stock < 0:
            raise forms.ValidationError('Количество не может быть отрицательным')
        return stock


