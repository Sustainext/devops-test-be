# Generated by Django 5.1.1 on 2024-10-24 06:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('esg_report', '0001_initial'),
        ('sustainapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutthecompanyandoperations',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='about_the_company_and_operations', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='aboutthereport',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='about_the_report', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='awardandrecognition',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='award_recognition', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='ceomessage',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ceo_message', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='esgreport',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='client_esg_reports', to='authentication.client'),
        ),
        migrations.AddField(
            model_name='esgreport',
            name='corporate_entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='esg_reports', to='sustainapp.corporateentity'),
        ),
        migrations.AddField(
            model_name='esgreport',
            name='framework',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='framework_esg_reports', to='sustainapp.framework'),
        ),
        migrations.AddField(
            model_name='esgreport',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='esg_reports', to='sustainapp.organization'),
        ),
        migrations.AddField(
            model_name='historicalaboutthecompanyandoperations',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalaboutthecompanyandoperations',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalaboutthereport',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalaboutthereport',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalawardandrecognition',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalawardandrecognition',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalceomessage',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalceomessage',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalmaterialitystatement',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmaterialitystatement',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalmissionvisionvalues',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmissionvisionvalues',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreeneleven',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreeneleven',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreenfifteenmodel',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreenfifteenmodel',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreenfourteen',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreenfourteen',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreennine',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreennine',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreenten',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreenten',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreenthirteen',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreenthirteen',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalscreentwelve',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalscreentwelve',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalstakeholderengagement',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalstakeholderengagement',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='historicalsustainabilityroadmap',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalsustainabilityroadmap',
            name='report',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='materialitystatement',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='materiality_statement', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='missionvisionvalues',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mission_vision_values', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screeneleven',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_eleven', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screenfifteenmodel',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_fifteen', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screenfourteen',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_fourteen', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screennine',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_nine', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screenten',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_ten', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screenthirteen',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_thirteen', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='screentwelve',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='screen_twelve', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='stakeholderengagement',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stakeholder_engagement', to='sustainapp.report'),
        ),
        migrations.AddField(
            model_name='sustainabilityroadmap',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sustainability_roadmap', to='sustainapp.report'),
        ),
    ]
