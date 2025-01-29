from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import datetime, timedelta
from .models import Evaluation
from classes.models import TeacherAssignment

def check_evaluation_due_dates():
    # Get all active teacher assignments
    assignments = TeacherAssignment.objects.filter(is_active=True).select_related('teacher', 'class_group')
    
    for assignment in assignments:
        learners = assignment.class_group.learners.filter(status='active')
        
        for learner in learners:
            # Check for 3-month evaluations
            last_3month = learner.evaluations.filter(evaluation_type='3month').order_by('-evaluation_date').first()
            # Check for 6-month evaluations
            last_6month = learner.evaluations.filter(evaluation_type='6month').order_by('-evaluation_date').first()
            
            today = datetime.now().date()
            
            # Check 3-month evaluations
            if not last_3month or (today - last_3month.evaluation_date) > timedelta(days=90):
                send_evaluation_reminder(
                    assignment.teacher,
                    learner,
                    '3month',
                    last_3month.evaluation_date if last_3month else None
                )
            
            # Check 6-month evaluations
            if not last_6month or (today - last_6month.evaluation_date) > timedelta(days=180):
                send_evaluation_reminder(
                    assignment.teacher,
                    learner,
                    '6month',
                    last_6month.evaluation_date if last_6month else None
                )

def send_evaluation_reminder(teacher, learner, eval_type, last_eval_date):
    subject = _('Υπενθύμιση Αξιολόγησης')
    
    context = {
        'teacher_name': teacher.get_full_name(),
        'learner_name': f"{learner.first_name} {learner.last_name}",
        'eval_type': '3μηνη' if eval_type == '3month' else '6μηνη',
        'last_eval_date': last_eval_date,
    }
    
    html_message = render_to_string('learners/email/evaluation_reminder.html', context)
    plain_message = render_to_string('learners/email/evaluation_reminder.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [teacher.email],
        html_message=html_message
    ) 