# Generated by Django 4.2.4 on 2024-12-12 08:50

import authentication.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sustainapp', '0006_department'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0007_remove_userprofile_department_and_more'),
        ('canadabills211', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('year', models.IntegerField(help_text='Year of the financial reporting year')),
                ('steps_taken_1', models.JSONField(help_text='1. What steps has the entity taken in the previous financial year to prevent and reduce the risk that forced labour or child labour is used at any step of the production of goods in Canada or elsewhere by the entity or of goods imported into Canada by the entity? Select all that apply', null=True)),
                ('steps_taken_description_1', models.TextField(blank=True, help_text='1. Other, please specify', max_length=1500, null=True)),
                ('additional_information_2', models.TextField(help_text='2. Please provide additional information describing the steps taken (if applicable)', max_length=1500, null=True)),
                ('structure_3', models.CharField(help_text='3.Which of the following accurately describes the entity’s structure?', max_length=255, null=True)),
                ('categorization_4', models.JSONField(help_text='4. Which of the following categorizations applies to the entity?', null=True)),
                ('additional_information_entity_5', models.TextField(help_text='5. Please provide additional information on the entity’s structure, activities and supply chains', max_length=1500, null=True)),
                ('policies_in_place_6', models.CharField(help_text='6.Does the entity currently have policies and due diligence processes in place related to forced labour and/or child labour?', max_length=16, null=True)),
                ('elements_implemented_6_1', models.JSONField(blank=True, help_text='6.1 If yes, which of the following elements of the due diligence process has the entity implemented in relation to forced labour and/or child labour?Select all that apply', null=True)),
                ('additional_info_policies_7', models.TextField(help_text='7. Please provide additional information on the entity’s policies and due diligence processes in relation to forced labour and child labour (if applicable)', max_length=1500, null=True)),
                ('risk_identified_8', models.CharField(help_text='8.Has the entity identified parts of its activities and supply chains that carry a risk of forced labour or child labour being used?', max_length=255, null=True)),
                ('risk_aspects_8_1', models.JSONField(help_text='8.1 If yes, has the entity identified forced labour or child labour risks related to any of the following aspects of its activities and supply chains? Select all that apply', null=True)),
                ('risk_aspects_description_8_1', models.TextField(blank=True, help_text='8.1 Other, please specify', max_length=255, null=True)),
                ('risk_activaties_9', models.JSONField(help_text='9. Has the entity identified forced labour or child labour risks in its activities and supply chains related to any of the following sectors and industries? Select all that apply', null=True)),
                ('risk_activaties_description_9', models.TextField(blank=True, help_text='9. Other, please specify', max_length=255, null=True)),
                ('additional_info_entity_10', models.CharField(help_text='10. Please provide additional information on the parts of the entity’s activities and supply chains that carry a risk of forced labour or child labour being used, as well as the steps that the entity has taken to assess and manage that risk (if applicable)', max_length=1500, null=True)),
                ('measures_remediate_activaties_11', models.TextField(help_text='11. Has the entity taken any measures to remediate any forced labour or child labour in its activities and supply chains?', max_length=255, null=True)),
                ('remediation_measures_taken_11_1', models.JSONField(help_text='11.1 If yes, which remediation measures has the entity taken? Select all that apply', null=True)),
                ('remediation_measures_taken_description_11_1', models.TextField(blank=True, help_text='11.1 Other, please specify', max_length=1500, null=True)),
                ('remediation_measures_12', models.CharField(help_text='12. Please provide additional information on any measures the entity has taken to remediate any forced labour or child labour (if applicable)', max_length=255, null=True)),
                ('measures_taken_loss_income_13', models.CharField(help_text='13. Has the entity taken any measures to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains?', max_length=1500, null=True)),
                ('additional_info_loss_income_14', models.TextField(help_text='14. Please provide additional information on any measures the entity has taken to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains (if applicable)', max_length=255, null=True)),
                ('training_provided_15', models.CharField(help_text='15. Does the entity currently provide training to employees on forced labour and/or child labour?', max_length=255, null=True)),
                ('training_mandatory_15_1', models.CharField(blank=True, help_text='15.1 If yes, is the training mandatory?', max_length=255, null=True)),
                ('additional_info_training_16', models.TextField(help_text='16. Please provide additional information on any measures the entity has taken to remediate the loss of income to the most vulnerable families that results from any measure taken to eliminate the use of forced labour or child labour in its activities and supply chains (if applicable)', max_length=1500, null=True)),
                ('policies_procedures_assess_17', models.CharField(help_text='17. Does the entity currently have policies and procedures in place to assess its effectiveness in ensuring that forced labour and child labour are not being used in its activities and supply chains?', max_length=16, null=True)),
                ('assessment_method_17_1', models.JSONField(blank=True, help_text='17.1 If yes, what method does the entity use to assess its effectiveness? Select all that apply', null=True)),
                ('assessment_method_description_17_1', models.TextField(blank=True, help_text='17.1 Other, please specify', max_length=1500, null=True)),
                ('additional_info_assessment_18', models.TextField(help_text='18. Please provide additional information on how the entity assesses its effectiveness in ensuring that forced labour and child labour are not being used in its activities and supply chains (if applicable)', max_length=1500, null=True)),
                ('client', models.ForeignKey(default=authentication.models.Client.get_default_client, on_delete=django.db.models.deletion.CASCADE, related_name='Annual_report_client', to='authentication.client')),
                ('corporate', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Annual_report_Corporate', to='sustainapp.corporateentity')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Annual_report_Organization', to='sustainapp.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Annaul_report', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='annualreport',
            constraint=models.UniqueConstraint(fields=('client', 'organization', 'corporate', 'year'), name='unique_annual_report'),
        ),
    ]
