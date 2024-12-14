import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django命令等待数据库可用"""

    def handle(self, *args, **options):
        self.stdout.write('等待数据库...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('数据库不可用，等待1秒...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('数据库可用！')) 