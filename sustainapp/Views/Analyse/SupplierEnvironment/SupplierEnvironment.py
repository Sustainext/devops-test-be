from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from datametric.models import RawResponse, DataPoint
from sustainapp.models import Corporateentity
from logging import getLogger

logger = getLogger("error.log")

class SupplierEnvAnlayzeView(APIView) :

    permission_classes = [IsAuthenticated]

    def calculate_percentage(self, q1, q2=None, filter_for_corp=False):

        if not filter_for_corp:

            return {
                "org_or_corp" : self.org.name if not self.corp else self.corp.name,
                "percentage" : (q1/q2)*100 if q2 !=0 else 0
            }
        
        else :

            return {
                "org_or_corp" : self.corprorate_of_org.name,
                "percentage" : (q1/q2)*100 if q2 !=0 else 0
            }

    def new_suppliers(self, path, filter_by, filter_for_corp=False) :

        lst = []

        sup_env_data = RawResponse.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
        ).first()

        if sup_env_data and path == "gri-supplier_environmental_assessment-new_suppliers-308-1a" :

            try :
                q1 = sup_env_data.data[0]["Q1"]
                q2 = sup_env_data.data[0]["Q2"]
                lst.append(self.calculate_percentage(float(q1), float(q2),filter_for_corp=filter_for_corp))
            except Exception as e :
                logger.error(f"SupplierEnvironment.py > the exception {e} for the path {path}")
                return []
            return lst

        elif sup_env_data and path in ["gri-supplier_environmental_assessment-negative_environmental-308-2d","gri-supplier_environmental_assessment-negative_environmental-308-2e"]:

            try :
                self.suppliers_assesed = RawResponse.objects.filter(
                    **filter_by,
                    path__slug="gri-supplier_environmental_assessment-negative_environmental-308-2a",
                    client_id=self.client_id,
                    year=self.year,
                ).first().data[0]["Q1"]

                q1 = sup_env_data.data[0]["Q1"]
                lst.append(self.calculate_percentage(float(q1), float(self.suppliers_assesed),filter_for_corp=filter_for_corp))
            except Exception as e :
                logger.error(f"SupplierEnvironment.py > the exception {e} for the path {path}")
                return []
            return lst
        
        elif not sup_env_data and self.corp is None :

            self.corp = True
            corps_of_org = Corporateentity.objects.filter(organization=self.org)
            result = []
            for corporate in corps_of_org:
                logger.error(f"SupplierEnvironment.py > checking for the corporate {corporate.name} with the path {path}")
                self.corprorate_of_org = corporate
                filtering = {
                    "organization__id" : self.org.id,
                    "corporate__id" : corporate.id
                }

                k = self.new_suppliers(path, filtering, filter_for_corp=True)
                if k != []:
                    result.extend(k)
            self.corp = None
            return result
        
        else :
            # No data exits
            return []

    def get (self, request ) :

        serialized_data = CheckOrgCoprDateSerializer(data=request.query_params)
        serialized_data.is_valid(raise_exception=True)
        try :
            self.org = serialized_data.validated_data["organisation"]
            self.corp = serialized_data.validated_data.get("corporate", None)
            self.from_date = serialized_data.validated_data["start"]
            self.to_date = serialized_data.validated_data["end"]

            if self.from_date.year == self.to_date.year:

                self.year = self.from_date.year

            else:

                logger.error(
                    "Analyze Environment > Suppliers Environmental Assessment : Start and End year should be same."
                )

                return Response(
                    {"error": "Start and End year should be same."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.client_id = request.user.client.id

            filter_by = {}

            filter_by["organization__id"] = self.org.id

            if self.corp is not None:

                filter_by["corporate__id"] = self.corp.id

            else:

                filter_by["corporate__id"] = None

            supplier_env_data = {}

            supplier_env_data['gri_308_1a'] = self.new_suppliers(
                "gri-supplier_environmental_assessment-new_suppliers-308-1a", filter_by
            )

            supplier_env_data["gri_308_2d"] = self.new_suppliers(
                    "gri-supplier_environmental_assessment-negative_environmental-308-2d",
                    filter_by
                )

            supplier_env_data['gri_308_2e'] = self.new_suppliers("gri-supplier_environmental_assessment-negative_environmental-308-2e", filter_by) 

            return Response(
                supplier_env_data,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"An error occured while analyzing Environment > Suppliers Environmental Assessment : {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
