import json, requests

from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import OnboardingSerializer


PLUGIN_ID = settings.PLUGIN_ID
ORGANISATION_ID = settings.ORGANISATION_ID

class OnboardingListView(APIView):

    serializer_class = OnboardingSerializer
    queryset = None

    def get(self, request, *args, **kwargs):
        url = f"https://api.zuri.chat/data/read/{PLUGIN_ID}/users/{ORGANISATION_ID}"
        response = requests.request("GET", url)
        print(response.status_code)
        if response.status_code == 200:
            r = response.json()
            serializer = OnboardingSerializer(data=r['data'], many=True)
            serializer.is_valid(raise_exception=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={"message": "Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OnboardingCreateView(APIView):

    serializer_class = OnboardingSerializer
    queryset = None

    def post(self, request, *args, **kwargs):
        url = "https://api.zuri.chat/data/write"
        company = request.data.get('company')
        sector = request.data.get('sector')
        position = request.data.get('position')
        data = {
            "plugin_id": PLUGIN_ID,
            "organization_id": ORGANISATION_ID,
            "collection_name": "users",
            "bulk_write": False,
            "payload": {
                "company": company,
                "sector": sector,
                "position": position
            }
        }
        response = requests.request("POST", url, data=json.dumps(data))
        r = response.json()
        print(response.status_code)
        print(r)
        if response.status_code == 201:
            return Response(data={'message': 'successful'}, status=status.HTTP_201_CREATED)
        return Response(data={"message": "Try again later"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)