from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from datametric.models import RawResponse
from sustainapp.models import Corporateentity
from logging import getLogger
from collections import defaultdict

logger = getLogger("error.log")

class CommunicationTrainingAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]


    def process_205_2a_2d(self, path, filter_by):

        def format_data(self, lst):
            res = []
            for obj in lst:
                try :
                    append_res = defaultdict(str)
                    append_res["loc"] = obj["Region Name"]
                    append_res["total_communicated"] = obj["Total number of governance body members that the organization's anti-corruption policies and procedures have been communicated to"]
                    append_res["total_region"] = obj["Total number of governance body members in that region."]
                    append_res["percentage"] = (float(append_res["total_communicated"])/float(append_res["total_region"])) * 100
                    res.append(append_res)
                except Exception as e:
                    logger.error(f"Error in Analyze Economic > Anti Corruption> CommunicationTraining : {e}")
                    continue
            return res
        raw_resp_205_2a = RawResponse.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
        ).first()

        if not raw_resp_205_2a and self.corp is None:
            logger.error(
                f"Economic/CommunicationTrainingAnalyzeView : There is no data for the organization {self.org} and the path {path} and the year {self.year}, So proceeding to check for its Corporates")
            corps_of_org = Corporateentity.objects.filter(organization=self.org)
            res_corps = []
            for corp in corps_of_org:
                raw_resp = RawResponse.objects.filter(
                    organization__id=self.org.id,
                    corporate__id=corp.id,
                    path__slug=path,
                    client_id=corp.client_id,
                    year=self.year,
                ).first()
                if raw_resp:
                    res_corps.extend(format_data(self, raw_resp.data[0]["Q1"]))
            return res_corps
            
        
        q1_lst =  raw_resp_205_2a.data[0]["Q1"]

        return format_data(self, q1_lst)
         
    def process_205_2b_2c_2d(self, path, filter_by):  

        def format_data_2b_2c_2d(self, raw_dict):
            
            for key,value in raw_dict.items():
                append_res = defaultdict(list)
                if value :
                    for item in value :
                        try : 
                            item['percentage'] = (float(item["Totalnumberemployees"])/float(item["Totalemployeeinthisregion"]))*100
                        except Exception as e:
                            logger.error(f"Error in Analyze Economic > Anti Corruption> CommunicationTraining : {e}")
                            continue
            return raw_dict
        
        raw_resp_205_2b_2c_2d = RawResponse.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
        ).first()
        
        if not raw_resp_205_2b_2c_2d and self.corp is None:
            logger.error(
                f"Economic/CommunicationTrainingAnalyzeView : There is no data for the organization {self.org} and the path {path} and the year {self.year}, So proceeding to check for its Corporates")
            corps_of_org = Corporateentity.objects.filter(organization=self.org)
            res_corps = []
            for corp in corps_of_org:
                raw_resp = RawResponse.objects.filter(
                    organization__id=self.org.id,
                    corporate__id=corp.id,
                    path__slug=path,
                    client_id=corp.client_id,
                    year=self.year,
                ).first()
                if raw_resp:
                    res_corps.extend(format_data_2b_2c_2d(self, raw_resp.data[0]["Q1"]))
            return res_corps
        if raw_resp_205_2b_2c_2d:
            return format_data_2b_2c_2d(self, raw_resp_205_2b_2c_2d.data[0]["Q1"])


    def get (self, request):
        serialized_data = CheckOrgCoprDateSerializer(data=request.query_params)
        serialized_data.is_valid(raise_exception=True)

        try:
            self.org = serialized_data.validated_data["organisation"]
            self.corp = serialized_data.validated_data.get("corporate", None)
            self.from_date = serialized_data.validated_data["start"]
            self.to_date = serialized_data.validated_data["end"]

            if self.from_date.year == self.to_date.year:
                self.year = self.from_date.year
            else:
                logger.error(
                    "Economic > Anti Corruption > Communication and Training - error: Start and End year should be same."
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

            data = defaultdict(list)
            data['analyze_205_2a'] = self.process_205_2a_2d(
                "gri-economic-anti_corruption-comm_and_training-205-2a-governance_body_members", filter_by
            )
            data['analyze_205_2d'] = self.process_205_2a_2d(
                "gri-economic-anti_corruption-comm_and_training-205-2d-training", filter_by
            )
            data['analyze_205_2b'] = self.process_205_2b_2c_2d(
                "gri-economic-anti_corruption-comm_and_training-205-2b-employees", filter_by,
            )
            data['analyze_205_2e'] = self.process_205_2b_2c_2d(
                "gri-economic-anti_corruption-comm_and_training-205-2e-policies", filter_by
            )
            data["analyze_205_2c"] = self.process_205_2b_2c_2d(
                "gri-economic-anti_corruption-comm_and_training-205-2c-business", filter_by
            )

            return Response(
                data,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"An error occured while analyzing Econoic > Anti Corruption > Communication and Training: {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)