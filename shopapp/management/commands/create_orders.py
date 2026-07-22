from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Product, Order


class Command(BaseCommand):
    help = 'Создание заказов через get_or_create'

    def handle(self, *args, **options):
        # Получаем или создаём тестового пользователя
        user, user_created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тестовый',
                'last_name': 'Пользователь',
            }
        )
        if user_created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Создан пользователь: {user.username} (пароль: testpass123)'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Пользователь уже существует: {user.username}'))

        # Получаем всех активных пользователей (для разнообразия)
        users = User.objects.all()
        products = Product.objects.filter(is_active=True)

        if not products.exists():
            self.stdout.write(self.style.ERROR('❌ Нет продуктов! Сначала запустите create_products.'))
            return

        orders_data = [
            {
                'comment': 'Срочный заказ, доставить как можно быстрее',
                'status': 'new',
                'products_names': ['Ноутбук Dell XPS 13', 'Мышь Logitech MX Master 3'],
            },
            {
                'comment': 'Подарок, нужна красивая упаковка',
                'status': 'processing',
                'products_names': ['Клавиатура Mechanical', 'Наушники Sony WH-1000XM5'],
            },
            {
                'comment': '',
                'status': 'completed',
                'products_names': ['Монитор Samsung 27"'],
            },
            {
                'comment': 'Самовывоз',
                'status': 'new',
                'products_names': ['Ноутбук Dell XPS 13', 'Клавиатура Mechanical', 'Мышь Logitech MX Master 3'],
            },
            {
                'comment': 'Тестовый заказ',
                'status': 'cancelled',
                'products_names': ['Смартфон iPhone 15 Pro'],
            },
        ]

        created_count = 0
        skipped_count = 0

        for order_data in orders_data:
            # Формируем уникальный идентификатор заказа (на основе комментария и продуктов)
            products_names_sorted = sorted(order_data['products_names'])
            order_identifier = f"{order_data['comment']}_{'_'.join(products_names_sorted)}"

            order, created = Order.objects.get_or_create(
                user=user,  # Для простоты используем одного пользователя
                comment=order_data['comment'],
                status=order_data['status'],
                defaults={'created_at': None}  # auto_now_add сработает автоматически
            )

            if created:
                # Добавляем продукты в заказ
                products_to_add = Product.objects.filter(name__in=order_data['products_names'])
                order.products.add(*products_to_add)
                created_count += 1

                total = order.get_total_price()
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Создан заказ #{order.id} на сумму {total} ₽ (товаров: {order.products.count()})'
                ))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'⚠️ Заказ уже существует: #{order.id}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Итог: создано {created_count} заказов, пропущено {skipped_count}'
        ))