# Generated by Django 5.1.5 on 2025-01-28 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learners', '0010_learner_disability_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='learner',
            name='additional_guardian_emails',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
