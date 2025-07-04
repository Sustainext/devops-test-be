# Generated by Django 4.2.4 on 2025-03-25 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0017_remove_organization_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='type_corporate_entity',
        ),
        migrations.AddField(
            model_name='organization',
            name='type_of_incorporation',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='address',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='city',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='countryoperation',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='currency',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='employeecount',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='location_of_headquarters',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='phone',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='revenue',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='sector',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='state',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='subindustry',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organization',
            name='website',
            field=models.CharField(default='Default', max_length=256),
            preserve_default=False,
        ),
    ]
