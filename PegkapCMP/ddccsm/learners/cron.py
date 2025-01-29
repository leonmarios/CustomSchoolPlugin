from django_crontab import CronJobBase, Schedule
from .notifications import check_evaluation_due_dates

class EvaluationReminderCron(CronJobBase):
    RUN_AT_TIMES = ['09:00']  # Run at 9 AM every day

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'learners.evaluation_reminder_cron'    # A unique code

    def do(self):
        check_evaluation_due_dates() 