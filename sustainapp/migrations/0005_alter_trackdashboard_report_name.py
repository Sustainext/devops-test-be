# Generated by Django 5.1.1 on 2024-10-30 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0004_alter_trackdashboard_report_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackdashboard',
            name='report_name',
            field=models.CharField(choices=[('emission', 'Emission'), ('energy', 'Energy'), ('waste', 'Waste'), ('employment', 'Employment'), ('ohs', 'Occupational Health and Safety (OHS)'), ('diversity_inclusion', 'Diversity & Inclusion'), ('community_development', 'Community Development'), ('water_and_effluents', 'Water & Effluents'), ('material', 'Material'), ('general', 'General'), ('economic', 'Economic'), ('governance', 'Governance')], max_length=1024),
        ),
    ]
