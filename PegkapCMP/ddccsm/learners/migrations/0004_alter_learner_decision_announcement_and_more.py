# Generated by Django 5.1.5 on 2025-01-28 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learners', '0003_socialhistory_additional_notes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='learner',
            name='decision_announcement',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ανακοίνωση Απόφασης'),
        ),
        migrations.AlterField(
            model_name='learner',
            name='emergency_phone',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Τηλ. Δ.Σ./ Έκτακτης Ανάγκης'),
        ),
        migrations.AlterField(
            model_name='learner',
            name='rv_team',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='RV Διεπιστημονική Ομάδα'),
        ),
    ]
