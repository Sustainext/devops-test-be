from django.core.management.base import BaseCommand
from sustainapp.models import Framework, Sdg, Certification, Regulation, Rating, Target


class Command(BaseCommand):
    # help = 'Loads initial data into the database'

    def handle(self, *args, **kwargs):

        models_to_check = [Certification, Framework, Rating, Regulation, Sdg, Target]
        models_with_existing_data = []
        for model in models_to_check:
            if model.objects.exists():
                self.stdout.write(
                    self.style.SUCCESS(f"Data already exists for model {model}")
                )
                models_with_existing_data.append(model)

        if models_with_existing_data:
            delete_choice = input(
                "Data already exists for the above models. Do you want to delete existing data and add? (yes/no): "
            )
            if delete_choice.lower() == "yes":
                for model in models_with_existing_data:
                    model.objects.all().delete()
            else:
                self.stdout.write(
                    self.style.WARNING("Operation aborted by user. Exiting...")
                )
                return

        # self.stdout.write(self.style.SUCCESS('Loading the data into Database'))

        Certification.objects.create(
            name="BCORP", Image="images/certifcations/BCorp_RZCvzp6.png"
        )
        Certification.objects.create(
            name="ISO 14001", Image="images/certifcations/ISO_14001_AyX5yip.png"
        )
        Certification.objects.create(
            name="UNGC", Image="images/certifcations/UNGC_Oe6Ede6.png"
        )

        Framework.objects.create(
            name="GRI: With reference to", Image="images/framework/GRI_icKvRwc.png"
        )
        Framework.objects.create(
            name="GRI: In accordance with", Image="images/framework/GRI_Vv3OtMS.png"
        )
        Framework.objects.create(name="CDP", Image="images/framework/CDP_6pVXNcF.png")
        Framework.objects.create(name="BRSR", Image="images/framework/SEBI_ijaHMOS.png")
        Framework.objects.create(name="SASB", Image="images/framework/SASB_doO0qoz.png")
        Framework.objects.create(name="TCFD", Image="images/framework/TCFD_igK4bk3.png")
        Framework.objects.create(
            name="UNPRI", Image="images/framework/UNPRI_gLQQO0p.png"
        )

        Rating.objects.create(name="DJSI", Image="images/rating/DJSI_yZCyi9R.png")
        Rating.objects.create(name="MSCI", Image="images/rating/MSCI_xXhLV4b.png")
        Rating.objects.create(
            name="SUSTAINALYTICS", Image="images/rating/SUSTAINALYTICS.png"
        )

        Regulation.objects.create(
            name="SB-253", Image="images/regulation/SB-253_OjG0XhP.png"
        )
        Regulation.objects.create(
            name="SB-261", Image="images/regulation/SB-261_1dJG1q5.png"
        )
        Regulation.objects.create(
            name="BILL S-211", Image="images/regulation/Bill_S-211.png"
        )
        Regulation.objects.create(name="GHGRP", Image="images/regulation/GHGRP.png")

        Sdg.objects.create(
            name="No Poverty",
            Image="images/sdg/E-WEB-Goal-01_w3iLQFp.png",
            Target_no=7,
            goal_no=1,
        )
        Sdg.objects.create(
            name="Zero Hunger",
            Image="images/sdg/E-WEB-Goal-02_PEdTrKf.png",
            Target_no=7,
            goal_no=2,
        )
        Sdg.objects.create(
            name="Good Health & Well-Being",
            Image="images/sdg/E-WEB-Goal-03_PcoVWT9.png",
            Target_no=7,
            goal_no=3,
        )
        Sdg.objects.create(
            name="Quality Education",
            Image="images/sdg/E-WEB-Goal-04_9ZpqV7e.png",
            Target_no=7,
            goal_no=4,
        )
        Sdg.objects.create(
            name="Gender Equality",
            Image="images/sdg/E-WEB-Goal-05_SM84Xa1.png",
            Target_no=7,
            goal_no=5,
        )
        Sdg.objects.create(
            name="Clean Water & Sanitation",
            Image="images/sdg/E-WEB-Goal-06_m3XADiN.png",
            Target_no=7,
            goal_no=6,
        )
        Sdg.objects.create(
            name="Affordable & Clean Energy",
            Image="images/sdg/E-WEB-Goal-07_eBXhTtg.png",
            Target_no=7,
            goal_no=7,
        )
        Sdg.objects.create(
            name="Decent Work & Economic Growth",
            Image="images/sdg/E-WEB-Goal-08_qsI9ovI.png",
            Target_no=7,
            goal_no=8,
        )
        Sdg.objects.create(
            name="Industry, Innovation & Infrastructure",
            Image="images/sdg/E-WEB-Goal-09_zv9AggO.png",
            Target_no=7,
            goal_no=9,
        )
        Sdg.objects.create(
            name="Reduced Inequalities",
            Image="images/sdg/E-WEB-Goal-10_VVSDI68.png",
            Target_no=7,
            goal_no=10,
        )
        Sdg.objects.create(
            name="Sustainable Cities And Communities",
            Image="images/sdg/E-WEB-Goal-11_8AuMlQR.png",
            Target_no=7,
            goal_no=11,
        )
        Sdg.objects.create(
            name="Responsible Consumption An Production",
            Image="images/sdg/E-WEB-Goal-12_3PW0ZHq.png",
            Target_no=7,
            goal_no=12,
        )
        Sdg.objects.create(
            name="Climate Action",
            Image="images/sdg/E-WEB-Goal-13_T2YCVhC.png",
            Target_no=7,
            goal_no=13,
        )
        Sdg.objects.create(
            name="Life Below Water",
            Image="images/sdg/E-WEB-Goal-14_BL41i3x.png",
            Target_no=7,
            goal_no=14,
        )
        Sdg.objects.create(
            name="Life On Land",
            Image="images/sdg/E-WEB-Goal-15_SSicEOp.png",
            Target_no=7,
            goal_no=15,
        )
        Sdg.objects.create(
            name="Peace, Justice And Strong Institutions",
            Image="images/sdg/E-WEB-Goal-16_E1KAPZA.png",
            Target_no=7,
            goal_no=16,
        )
        Sdg.objects.create(
            name="Partnership For The Goals",
            Image="images/sdg/E-WEB-Goal-17_5zRe7fI.png",
            Target_no=7,
            goal_no=17,
        )

        Target.objects.create(
            name="SBTi", Image="images/Target/E-WEB-Target-01_w3iLQFp.png"
        )
        Target.objects.create(
            name="SBTi Net Zero", Image="images/Target/SBTi_lnygnBi.png"
        )

        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))
