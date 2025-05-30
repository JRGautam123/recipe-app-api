"""
Django command to wait for the database to be availabale
"""

from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database"""
    def handle(self, *args, **options):
        """Entry Point for Command"""
        self.stdout.write('Waiting for database....')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (psycopg2Error, OperationalError):
                self.stdout.write("Databse unavailable,"
                                  "waiting for 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available'))
