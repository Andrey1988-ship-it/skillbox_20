
from django.contrib import admin
from .models import Product, Order, OrderItem, UploadedFile


# Inline для отображения заказов на странице продукта
class OrderItemInline(admin.TabularInline):
    """Отображение заказов, в которых используется этот продукт"""
    model = OrderItem
    extra = 0
    verbose_name = "Заказ"
    verbose_name_plural = "📦 Заказы с этим товаром"
    fields = ('order', 'quantity', 'price')
    readonly_fields = ('order',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


# Inline для отображения товаров в заказе (ДОБАВЛЕНО!)
class ProductItemInline(admin.TabularInline):
    """Отображение товаров в заказе"""
    model = OrderItem
    extra = 1
    verbose_name = "Товар"
    verbose_name_plural = "🛍️ Товары в заказе"
    fields = ('product', 'quantity', 'price', 'get_cost')
    readonly_fields = ('get_cost',)

    def get_cost(self, obj):
        return f"{obj.get_cost():.2f} руб."

    get_cost.short_description = "Стоимость"


class ProductAdmin(admin.ModelAdmin):
    """Настройка отображения модели Product в админке"""

    list_display = ('name', 'price', 'discount', 'stock', 'is_active', 'is_archived', 'created_at')
    search_fields = ('name', 'description', 'price', 'discount', 'stock')
    list_display_links = ('name',)
    list_filter = ('is_active', 'is_archived', 'created_at', 'price', 'stock')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Цена и скидка', {
            'fields': ('price', 'discount'),
            'classes': ('wide',)
        }),
        ('Учет на складе', {
            'fields': ('stock', 'is_active'),
            'classes': ('wide',)
        }),
        ('Дополнительные опции', {
            'fields': ('image', 'is_archived'),
            'classes': ('collapse',),
            'description': 'Настройки изображения и архивации'
        }),
    )

    # Показываем заказы, в которых есть этот продукт
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

    actions = ['archive_products', 'unarchive_products']

    def archive_products(self, request, queryset):
        count = queryset.update(is_archived=True)
        self.message_user(request, f'✅ {count} продукт(ов) успешно архивирован(ы)')

    archive_products.short_description = "Архивировать выбранные продукты"

    def unarchive_products(self, request, queryset):
        count = queryset.update(is_archived=False)
        self.message_user(request, f'✅ {count} продукт(ов) успешно разархивирован(ы)')

    unarchive_products.short_description = "Разархивировать выбранные продукты"


class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения модели Order в админке"""

    list_display = ('id', 'first_name', 'last_name', 'phone', 'status', 'created_at', 'get_total_price')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'id')
    list_filter = ('status', 'created_at', 'updated_at')
    list_display_links = ('id', 'first_name')

    # 🔥 ВАЖНО: Добавляем inline для отображения товаров в заказе
    inlines = [ProductItemInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Информация о доставке', {
            'fields': ('address', 'comment'),
            'classes': ('wide',)
        }),
        ('Статус заказа', {
            'fields': ('status',),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_total_price(self, obj):
        """Общая стоимость заказа"""
        total = sum(item.get_cost() for item in obj.items.all())
        return f"{total:.2f} руб."

    get_total_price.short_description = "Общая сумма"


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'file_size', 'content_type', 'uploaded_at', 'uploaded_by')
    list_filter = ('content_type', 'uploaded_at')
    search_fields = ('file', 'description')
    readonly_fields = ('file_size', 'content_type', 'uploaded_at')

# Регистрируем модели
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)