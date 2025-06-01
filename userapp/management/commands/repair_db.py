from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Repairs the crashed MySQL table'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Repair the user_answers table
                cursor.execute("REPAIR TABLE user_answers")
                self.stdout.write(self.style.SUCCESS('Successfully repaired user_answers table'))
                
                # Check table status
                cursor.execute("CHECK TABLE user_answers")
                result = cursor.fetchone()
                self.stdout.write(f"Table status: {result[2]}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error repairing table: {str(e)}')) 