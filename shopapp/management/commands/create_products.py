from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    help = 'Создание продуктов через get_or_create'

    def handle(self, *args, **options):
        products_data = [
            {'name': 'Брелок "Котик"', 'slug': 'brelok-kotik', 'description': 'Милый брелок в виде котика', 'price': 299.00, 'stock': 15, 'discount': 0, 'is_active': True},
            {'name': 'Брелок "Сердечко"', 'slug': 'brelok-serdechko', 'description': 'Романтичный брелок-сердечко', 'price': 199.00, 'stock': 20, 'discount': 0, 'is_active': True},
            {'name': 'Брелок "Машинка"', 'slug': 'brelok-mashinka', 'description': 'Брелок в форме автомобиля', 'price': 349.00, 'stock': 10, 'discount': 0, 'is_active': True},
            {'name': 'Брелок "Смайлик"', 'slug': 'brelok-smaylik', 'description': 'Веселый брелок-смайлик', 'price': 149.00, 'stock': 30, 'discount': 5, 'is_active': True},
            {'name': 'Брелок "Звезда"', 'slug': 'brelok-zvezda', 'description': 'Брелок в виде звезды', 'price': 249.00, 'stock': 25, 'discount': 10, 'is_active': True},
        ]

        created = 0
        for data in products_data:
            product, is_created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'slug': data['slug'],
                    'description': data['description'],
                    'price': data['price'],
                    'stock': data['stock'],
                    'discount': data['discount'],
                    'is_active': data['is_active'],
                }
            )
            if is_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создан: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Уже существует: {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n📊 Создано продуктов: {created}'))