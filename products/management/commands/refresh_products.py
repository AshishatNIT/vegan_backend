from django.core.management.base import BaseCommand
from django.core.management import call_command
from products.models import Product

class Command(BaseCommand):
    help = 'Deletes all products and re-imports from master CSV.'

    def handle(self, *args, **options):
        # 1. Delete all existing products
        self.stdout.write(self.style.WARNING('Deleting all existing products...'))
        count, _ = Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} products.'))
        
        # 2. Call the import_products command
        self.stdout.write('Running import_products command...')
        call_command('import_products')
        
        self.stdout.write(self.style.SUCCESS('Data refresh complete!'))