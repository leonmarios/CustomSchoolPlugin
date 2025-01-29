from django.core.management.base import BaseCommand
from learners.notifications import check_evaluation_due_dates

class Command(BaseCommand):
    help = 'Sends evaluation reminder emails to teachers'

    def handle(self, *args, **options):
        self.stdout.write('Starting to send evaluation reminders...')
        try:
            check_evaluation_due_dates()
            self.stdout.write(self.style.SUCCESS('Successfully sent evaluation reminders'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending reminders: {str(e)}')) 