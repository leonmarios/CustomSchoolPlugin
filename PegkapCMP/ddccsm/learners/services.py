from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, ExtractYear
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Learner, AuditLog
from django.contrib.contenttypes.models import ContentType

class LearnerStatistics:
    def __init__(self):
        self.now = timezone.now()
        self.current_year = self.now.year
        self.last_year = self.current_year - 1

    def get_total_learners(self):
        return {
            'total': Learner.objects.count(),
            'active': Learner.objects.filter(is_active=True).count(),
            'inactive': Learner.objects.filter(is_active=False).count()
        }

    def get_monthly_registrations(self):
        """Get monthly registrations for the current year"""
        return (Learner.objects
                .filter(created_at__year=self.current_year)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month'))

    def get_age_distribution(self):
        """Get age distribution of learners"""
        age_ranges = {
            '0-18': Q(dynamic_fields__age__lt=18),
            '18-25': Q(dynamic_fields__age__range=(18, 25)),
            '26-35': Q(dynamic_fields__age__range=(26, 35)),
            '36-50': Q(dynamic_fields__age__range=(36, 50)),
            '50+': Q(dynamic_fields__age__gt=50)
        }
        
        distribution = {}
        for range_name, query in age_ranges.items():
            distribution[range_name] = Learner.objects.filter(query).count()
        
        return distribution

    def get_class_distribution(self):
        """Get distribution by class assignment"""
        return (Learner.objects
                .filter(is_active=True)
                .values('dynamic_fields__class_assignment')
                .annotate(count=Count('id'))
                .order_by('-count'))

    def get_expiring_documents(self, days=30):
        """Get learners with documents expiring soon"""
        threshold_date = self.now.date() + timedelta(days=days)
        
        expiring_fields = [
            'eopyy_expiry',
            'kepa_expiry',
            'insurance_expiry'
        ]
        
        expiring = []
        for field in expiring_fields:
            field_query = {f'dynamic_fields__{field}__lte': threshold_date}
            learners = (Learner.objects
                       .filter(is_active=True, **field_query)
                       .values('id', 'first_name', 'last_name', 
                              f'dynamic_fields__{field}'))
            for learner in learners:
                expiring.append({
                    'learner': f"{learner['first_name']} {learner['last_name']}",
                    'document': field.replace('_expiry', '').upper(),
                    'expiry_date': learner[f'dynamic_fields__{field}']
                })
        
        return sorted(expiring, key=lambda x: x['expiry_date'])

    def get_all_statistics(self):
        """Get all statistics in one call"""
        return {
            'totals': self.get_total_learners(),
            'monthly_registrations': self.get_monthly_registrations(),
            'age_distribution': self.get_age_distribution(),
            'class_distribution': self.get_class_distribution(),
            'expiring_documents': self.get_expiring_documents()
        }

class AuditLogger:
    @staticmethod
    def log_action(user, action, instance, changes=None, ip_address=None):
        """Log an action in the audit log"""
        content_type = ContentType.objects.get_for_model(instance)
        
        return AuditLog.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.pk,
            changes=changes,
            ip_address=ip_address
        )

    @staticmethod
    def get_changes(old_data, new_data):
        """Compare old and new data to get changes"""
        changes = {}
        
        for key in new_data:
            if key in old_data and old_data[key] != new_data[key]:
                changes[key] = {
                    'old': old_data[key],
                    'new': new_data[key]
                }
                
        return changes if changes else None 