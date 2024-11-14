from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from sustainapp.Serializers.CheckOrgCorpDateSerializer import CheckOrgCoprDateSerializer
from datametric.models import RawResponse
from sustainapp.models import Corporateentity
from logging import getLogger

logger = getLogger("error.log")
class MarketPresenceAnalyseView(APIView):
    permission_classes = [IsAuthenticated]

    def format_data(self, raw_resp_1a, currency : float) -> list :
        #What if they don't add the values in male and female
        res =[]
        for obj in raw_resp_1a.data[0]["Q4"]:
            try : 
                obj["Male"] = float(obj["Male"])/currency
                obj["Female"] = float(obj["Female"])/currency
                obj["Non-binary"] = float(obj["Non-binary"])/currency
                res.append(obj)
            except Exception as e:
                logger.error(f"Analyze Economic Market Precesnse error : {e}")
                continue
        
        return res

    def process_market_presence(self, path, filter_by):

        raw_resp_1a = RawResponse.objects.filter(
            **filter_by,
            path__slug=path,
            client_id=self.client_id,
            year=self.year,
            ).first()
        
        raw_resp_1c = RawResponse.objects.filter(
            **filter_by,
            path__slug="gri-economic-ratios_of_standard_entry-202-1c-location",
            client_id=self.client_id,
            year=self.year,
            ).first()
        if raw_resp_1a and raw_resp_1c:
            if raw_resp_1a.data[0]["Q4"] and raw_resp_1a.data[0]["Q3"] == raw_resp_1c.data[0]["Currency"].split(" ")[1]:
                currency = float(raw_resp_1c.data[0]["Currency"].split(" ")[0])
                return self.format_data(raw_resp_1a, currency)  
            else :
                raise KeyError ("Please add data and also match the currency")
            
        elif not raw_resp_1a and not raw_resp_1c and  self.corp is None:
            logger.error(
                f"Economic/MarketPresenceAnalyse : There is no data for the organization {self.org} and the path {path} and the year {self.year}, So proceeding to check for its Corporates"
            )
            corps_of_org = Corporateentity.objects.filter(organization__id=self.org.id)
            corp_res = []
            for corp in corps_of_org :
                
                raw_resp_1a = RawResponse.objects.filter(
                    organization__id=self.org.id,
                    corporate__id=corp.id,
                    path__slug=path,
                    client_id=self.client_id,
                    year=self.year,
                ).first()
                raw_resp_1c = RawResponse.objects.filter(
                    organization__id=self.org.id,
                    corporate__id=corp.id,
                    path__slug="gri-economic-ratios_of_standard_entry-202-1c-location",
                    client_id=self.client_id,
                    year=self.year,
                ).first()
            
                if raw_resp_1a and raw_resp_1c :
                    corp_res.extend(self.format_data(raw_resp_1a, float(raw_resp_1c.data[0]["Currency"].split(" ")[0])))
            
            return corp_res

        else : 
            #There is no data added
            return []

    def get(self, request):

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
                    "Economic/Market Presence/Ratio of entry level wages - error: Start and End year should be same."
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

            marketing_presence_ratio = self.process_market_presence(
                "gri-economic-ratios_of_standard_entry_level_wage_by_gender_compared_to_local_minimum_wage-202-1a-s1", filter_by
            )

            return Response(
                {"marketing_presence": marketing_presence_ratio},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(
                f"An error occured while analyzing General/Collective Bargaining: {e}"
            )
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)