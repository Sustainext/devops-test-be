from django.core.management.base import BaseCommand
from sustainapp.models import Framework, Sdg, Certification, Regulation, Rating, Target
 
 
class Command(BaseCommand):
    # help = 'Loads initial data into the database'
 
    def handle(self, *args, **kwargs):
 
        models_to_check = [Certification, Framework, Rating, Regulation, Sdg, Target]
 
        for model in models_to_check:
            if model.objects.exists():
                self.stdout.write(
                    self.style.SUCCESS(f"Data already exists for model {model}")
                )
 
        self.update_or_create_certifications()
        self.update_or_create_frameworks()
        self.update_or_create_ratings()
        self.update_or_create_regulations()
        self.update_or_create_sdgs()
        self.update_or_create_targets()
 
        self.stdout.write(self.style.SUCCESS("Data Updated successfully"))
 
    def update_or_create_certifications(self):
        certifications = [
            {"id": 1, "name": "BCORP", "Image": "images/certifications/BCorp.png"},
            {
                "id": 2,
                "name": "ISO 14001",
                "Image": "images/certifications/ISO_14001.png",
            },
            {"id": 3, "name": "UNGC", "Image": "images/certifications/UNGC.png"},
        ]
        for cert in certifications:
            Certification.objects.update_or_create(id=cert["id"], defaults=cert)
 
    def update_or_create_frameworks(self):
        frameworks = [
            {
                "id": 1,
                "name": "GRI: With reference to",
                "Image": "images/framework/GRI.png",
            },
            {
                "id": 2,
                "name": "GRI: In accordance with",
                "Image": "images/framework/GRI.png",
            },
            {"id": 3, "name": "CDP", "Image": "images/framework/CDP.png"},
            {"id": 4, "name": "BRSR", "Image": "images/framework/SEBI.png"},
            {"id": 5, "name": "SASB", "Image": "images/framework/SASB.png"},
            {"id": 6, "name": "TCFD", "Image": "images/framework/TCFD.png"},
            {"id": 7, "name": "UNPRI", "Image": "images/framework/UNPRI.png"},
        ]
        for framework in frameworks:
            Framework.objects.update_or_create(id=framework["id"], defaults=framework)
 
    def update_or_create_ratings(self):
        ratings = [
            {"id": 1, "name": "DJSI", "Image": "images/rating/DJSI.png"},
            {"id": 2, "name": "MSCI", "Image": "images/rating/MSCI.png"},
            {
                "id": 3,
                "name": "SUSTAINALYTICS",
                "Image": "images/rating/SUSTAINALYTICS.png",
            },
        ]
        for rating in ratings:
            Rating.objects.update_or_create(id=rating["id"], defaults=rating)
 
    def update_or_create_regulations(self):
        regulations = [
            {"id": 1, "name": "SB-253", "Image": "images/regulation/SB-253.png"},
            {"id": 2, "name": "SB-261", "Image": "images/regulation/SB-261.png"},
            {
                "id": 3,
                "name": "BILL S-211",
                "Image": "images/regulation/Bill_S-211.png",
            },
            {"id": 4, "name": "GHGRP", "Image": "images/regulation/GHGRP.png"},
        ]
        for regulation in regulations:
            Regulation.objects.update_or_create(
                id=regulation["id"], defaults=regulation
            )
 
    def update_or_create_sdgs(self):
        sdgs = [
            {
                "id": 1,
                "name": "No Poverty",
                "Image": "images/sdg/E-WEB-Goal-01.png",
                "Target_no": 7,
                "goal_no": 1,
            },
            {
                "id": 2,
                "name": "Zero Hunger",
                "Image": "images/sdg/E-WEB-Goal-02.png",
                "Target_no": 7,
                "goal_no": 2,
            },
            {
                "id": 3,
                "name": "Good Health & Well-Being",
                "Image": "images/sdg/E-WEB-Goal-03.png",
                "Target_no": 7,
                "goal_no": 3,
            },
            {
                "id": 4,
                "name": "Quality Education",
                "Image": "images/sdg/E-WEB-Goal-04.png",
                "Target_no": 7,
                "goal_no": 4,
            },
            {
                "id": 5,
                "name": "Gender Equality",
                "Image": "images/sdg/E-WEB-Goal-05.png",
                "Target_no": 7,
                "goal_no": 5,
            },
            {
                "id": 6,
                "name": "Clean Water & Sanitation",
                "Image": "images/sdg/E-WEB-Goal-06.png",
                "Target_no": 7,
                "goal_no": 6,
            },
            {
                "id": 7,
                "name": "Affordable & Clean Energy",
                "Image": "images/sdg/E-WEB-Goal-07.png",
                "Target_no": 7,
                "goal_no": 7,
            },
            {
                "id": 8,
                "name": "Decent Work & Economic Growth",
                "Image": "images/sdg/E-WEB-Goal-08.png",
                "Target_no": 7,
                "goal_no": 8,
            },
            {
                "id": 9,
                "name": "Industry, Innovation & Infrastructure",
                "Image": "images/sdg/E-WEB-Goal-09.png",
                "Target_no": 7,
                "goal_no": 9,
            },
            {
                "id": 10,
                "name": "Reduced Inequalities",
                "Image": "images/sdg/E-WEB-Goal-10.png",
                "Target_no": 7,
                "goal_no": 10,
            },
            {
                "id": 11,
                "name": "Sustainable Cities And Communities",
                "Image": "images/sdg/E-WEB-Goal-11.png",
                "Target_no": 7,
                "goal_no": 11,
            },
            {
                "id": 12,
                "name": "Responsible Consumption An Production",
                "Image": "images/sdg/E-WEB-Goal-12.png",
                "Target_no": 7,
                "goal_no": 12,
            },
            {
                "id": 13,
                "name": "Climate Action",
                "Image": "images/sdg/E-WEB-Goal-13.png",
                "Target_no": 7,
                "goal_no": 13,
            },
            {
                "id": 14,
                "name": "Life Below Water",
                "Image": "images/sdg/E-WEB-Goal-14.png",
                "Target_no": 7,
                "goal_no": 14,
            },
            {
                "id": 15,
                "name": "Life On Land",
                "Image": "images/sdg/E-WEB-Goal-15.png",
                "Target_no": 7,
                "goal_no": 15,
            },
            {
                "id": 16,
                "name": "Peace, Justice And Strong Institutions",
                "Image": "images/sdg/E-WEB-Goal-16.png",
                "Target_no": 7,
                "goal_no": 16,
            },
            {
                "id": 17,
                "name": "Partnership For The Goals",
                "Image": "images/sdg/E-WEB-Goal-17.png",
                "Target_no": 7,
                "goal_no": 17,
            },
        ]
        for sdg in sdgs:
            Sdg.objects.update_or_create(id=sdg["id"], defaults=sdg)
 
    def update_or_create_targets(self):
        targets = [
            {"id": 1, "name": "SBTi", "Image": "images/Target/SBTi.png"},
            {"id": 2, "name": "SBTi Net Zero", "Image": "images/Target/SBTi.png"},
        ]
        for target in targets:
            Target.objects.update_or_create(id=target["id"], defaults=target)