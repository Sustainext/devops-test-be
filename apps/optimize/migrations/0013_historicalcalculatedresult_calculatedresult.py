# Generated by Django 4.2.4 on 2025-04-30 10:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('optimize', '0012_remove_historicalselectedactivity_calculated_results_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalCalculatedResult',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('year', models.PositiveIntegerField()),
                ('activity_name', models.CharField(max_length=255)),
                ('activity_id', models.CharField(max_length=255)),
                ('metric', models.CharField(max_length=100)),
                ('result', models.JSONField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('scenario', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='optimize.scenerio')),
            ],
            options={
                'verbose_name': 'historical calculated result',
                'verbose_name_plural': 'historical calculated results',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='CalculatedResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('year', models.PositiveIntegerField()),
                ('activity_name', models.CharField(max_length=255)),
                ('activity_id', models.CharField(max_length=255)),
                ('metric', models.CharField(max_length=100)),
                ('result', models.JSONField()),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calculated_results', to='optimize.scenerio')),
            ],
            options={
                'indexes': [models.Index(fields=['scenario', 'year'], name='optimize_ca_scenari_da6fed_idx'), models.Index(fields=['activity_id'], name='optimize_ca_activit_e102d9_idx')],
            },
        ),
    ]
