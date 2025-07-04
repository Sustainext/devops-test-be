# Generated by Django 4.2 on 2025-05-08 07:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sustainapp', '0023_alter_corporateentity_employeecount_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(2000)])),
                ('screen', models.IntegerField()),
                ('data', models.JSONField()),
                ('corporate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sustainapp.corporateentity')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sustainapp.organization')),
            ],
            options={
                'verbose_name': 'Submission Information for Canada Bill S211 2025',
                'verbose_name_plural': 'Submission Information for Canada Bill S211 2025',
                'ordering': ['created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalSubmissionInformation',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('year', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(2000)])),
                ('screen', models.IntegerField()),
                ('data', models.JSONField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('corporate', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.corporateentity')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.organization')),
            ],
            options={
                'verbose_name': 'historical Submission Information for Canada Bill S211 2025',
                'verbose_name_plural': 'historical Submission Information for Canada Bill S211 2025',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalReportingForEntities',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('year', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(2000)])),
                ('screen', models.IntegerField()),
                ('data', models.JSONField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('corporate', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.corporateentity')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.organization')),
            ],
            options={
                'verbose_name': 'historical Reporting For Entities',
                'verbose_name_plural': 'historical Reporting For Entities',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ReportingForEntities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(validators=[django.core.validators.MaxValueValidator(2100), django.core.validators.MinValueValidator(2000)])),
                ('screen', models.IntegerField()),
                ('data', models.JSONField()),
                ('corporate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sustainapp.corporateentity')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sustainapp.organization')),
            ],
            options={
                'verbose_name': 'Reporting For Entities',
                'verbose_name_plural': 'Reporting For Entities',
                'ordering': ['created_at'],
                'abstract': False,
                'unique_together': {('organization', 'corporate', 'year', 'screen')},
            },
        ),
    ]
