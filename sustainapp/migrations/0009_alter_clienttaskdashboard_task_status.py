# Generated by Django 4.2.4 on 2025-01-17 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0008_clienttaskdashboard_comments_assignee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienttaskdashboard',
            name='task_status',
            field=models.CharField(choices=[('in_progress', 'in_progress'), ('approved', 'approved'), ('under_review', 'under_review'), ('completed', 'completed'), ('reject', 'reject'), ('not_started', 'not_started')], default='not_started', max_length=64),
        ),
    ]
