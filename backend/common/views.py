import requests, json

from django.http import Http404
from django.conf import settings
# from django.views.static import serve as static_serve

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .json_data import *

### api/v1/sidebar?org=5336&user=Devjoseph&token=FGEZJJ-ZFDGB-FDGG
PLUGIN_ID = settings.PLUGIN_ID
ORGANISATION_ID = settings.ORGANISATION_ID


class SidebarView(APIView):
    def get(self, request, *args, **kwargs):
        data = success_query()
        return Response(data, status=status.HTTP_200_OK)

class RoomSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    room_name = serializers.CharField()


def is_valid(param):
    return param != "" and param is not None

class InfoView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            "message": "Plugin Information Retrieved",
            "data": {
                "type": "Plugin Information",
                "plugin_info": {
                "name": "Sales Prospects Plugin",
                "description": [
                "Zuri.chat plugin",
                "A plugin for Zuri Chat that enables the users to get prospects for their respective businesses "
                ]
                },
                "scaffold_structure": "Monolith",
                "team": "HNG 8.0/Team plugin sales-crm",
                "sidebar_url": "https://sales.zuri.chat/api/v1/sidebar",
                "ping_url": "https://sales.zuri.chat/api/v1/ping",
                "homepage_url": "https://sales.zuri.chat/"
                },
                "success": True
        }
        return Response(data=data, status=status.HTTP_200_OK)


class AddUserToRoom(APIView):
    serializer_class = RoomSerializer
    @extend_schema(
        description = "Room Name (str) : The name of the room\
            User Id (int): The id of the user to be added to the rooom\n\
            This view creates a room if there isn't a room that has the specified name\n\
            If there's a room with the name specified, the room's members are merely updated\
            in the sense that the userId supplied is added to the room.\n"
    )
    def post(self, request, *args, **kwargs):

        room_name = request.data.get('room_name')
        user = request.data.get('user')
        if not is_valid(user):
            raise Http404("user_id not supplied")
        if not is_valid(room_name):
            raise Http404("room_name not supplied")
        method = "POST"
        current_users = []
        object_id = None
        get_url = f"https://api.zuri.chat/data/read/{PLUGIN_ID}/sales_room/{ORGANISATION_ID}"
        res = requests.request("GET", url=get_url)
        if res.status_code == 200 and is_valid(res.json().get('data')):
            rooms = res.json()['data']

            current_room = filter(lambda room: room['name'] == room_name, rooms)
            current_room = list(current_room)

            if len(current_room) > 0:
                method = "PUT"
                object_id = current_room[0]['_id']
                current_users = current_room[0]['users']

        current_users.append(user)
        current_users = list(set(current_users))

        post_url = 'https://api.zuri.chat/data/write'
        data = {
            "plugin_id": "613b677d41f5856617552f1e",
            "organization_id": "613a495f59842c7444fb0246",
            "collection_name": "sales_room",
            "object_id": object_id,
            "bulk_write": False,
            "payload": {
                "name": room_name,
                "users": current_users
            }
        }
        res = requests.request(method, url=post_url, data=json.dumps(data))

        if res.status_code in [201, 200]:

            response = {
                "message": "successful",
                "room_name": room_name,
                "members": current_users,
                "rooms":"http://sales.zuri.chat/api/v1/rooms/"
            }
            return Response(data=response, status=status.HTTP_200_OK)

        return Response(data={"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoomsListView(APIView):
    def get(self, request, *args, **kwargs):
        get_url = f"https://api.zuri.chat/data/read/{PLUGIN_ID}/sales_room/{ORGANISATION_ID}"
        res = requests.request("GET", url=get_url)
        print(res.json())
        if res.status_code == 200 and is_valid(res.json().get('data')):
            return Response(data=res.json()['data'], status=status.HTTP_200_OK)
        return Response(data={"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveUserFromRoom(APIView):
 
         
    serializer_class = RoomSerializer
    def post(self, request, *args, **kwargs):
        
    # url to fetch all rooms
        get_url = f"https://api.zuri.chat/data/read/{PLUGIN_ID}/sales_room/{ORGANISATION_ID}"
        
        # make a get request to the url to fetch all existing rooms 
        
        user_to_remove = request.data.get('user')
        room_name = request.data.get('room_name')
        
        res = requests.request("GET", url=get_url)
        if res.status_code != 200:
            return Response(data={"message": "error occur while retrieving data for all rooms"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #    extract rooms from the response
        rooms = res.json()['data']
        
        current_room = filter(lambda room: room['name'] == room_name, rooms)
        current_room = list(current_room)
        print(current_room)
        if len(current_room) == 0:
            return Response(data={"message": "Room does not exist"}, status=status.HTTP_404_NOT_FOUND)
        method = "PUT"
        object_id = current_room[0]['_id']
        current_users = current_room[0]['users']
        print(user_to_remove , current_users)
        
        if (user_to_remove in current_users):
            #  return Response(data={"message": "This user does not belong to this room"}, status=status.HTTP_404_NOT_FOUND)
            current_users.remove(user_to_remove)
            print(current_users)
            #   current_users = set(current_users)
            put_url = 'https://api.zuri.chat/data/write'
            data = {
                    "plugin_id": PLUGIN_ID,
                    "organization_id": ORGANISATION_ID,
                    "collection_name": "sales_room",
                    "object_id": object_id,
                    "bulk_write": False,
                    "payload": {
                        "name": room_name,
                        "users": current_users
                    }
                }
            res = requests.request(method, url=put_url, data=json.dumps(data))
            if res.status_code in [201, 200]:
                return Response(data={"message":"user "+ user_to_remove + " has been removed from room "+ room_name}, status=status.HTTP_200_OK)
            return Response(data={"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={"message": "This user does not exist to this room"}, status=status.HTTP_404_NOT_FOUND)

#
# class DeleteUserToRoom(APIView):
#     serializer_class = RoomSerializer
#
#     def post(self, request, *args, **kwargs):
#
#         room_name = request.data.get('room_name')
#         user = request.data.get('user')
#         if not is_valid(user):
#             raise Http404("user_id not supplied")
#         if not is_valid(room_name):
#             raise Http404("room_name not supplied")
#
#         current_users = []
#         object_id = None
#         get_url = "https://api.zuri.chat/data/read/613b677d41f5856617552f1e/sales_room/613a495f59842c7444fb0246"
#         res = requests.request("GET", url=get_url)
#         if res.status_code == 200 and is_valid(res.json()['data']):
#             rooms = res.json()['data']
#
#             current_room = filter(lambda room: room['name'] == room_name, rooms)
#             current_room = list(current_room)
#
#             if len(current_room) > 0:
#                 current_users.append(user)
#                 current_users = list(set(current_users))
#                 REMOVE THE ID FROM THE CURRENT USERS OF THAT ROOM THEN UPDATE THE ROOM WITH THE CURRENT USERS
#                 post_url = 'https://api.zuri.chat/data/write'
#                 data = {
#                     "plugin_id": "613b677d41f5856617552f1e",
#                     "organization_id": "613a495f59842c7444fb0246",
#                     "collection_name": "sales_room",
#                     "object_id": object_id,
#                     "bulk_write": False,
#                 }
#                 res = requests.request("DELETE", url=post_url, data=json.dumps(data))
#
#                 if res.status_code in [201, 200]:
#                     response = {
#                         "message": "successful",
#                         "room_name": room_name,
#                         "members": current_users
#                     }
#                     return Response(data=response, status=status.HTTP_200_OK)
#
#         return Response(data={"message": "failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def serve(request, path, document_root=None, show_indexes=False):
#     """
#     An override to `django.views.static.serve` that will allow us to add our
#     own headers for development.

#     Like `django.views.static.serve`, this should only ever be used in
#     development, and never in production.
#     """
#     response = static_serve(request, path, document_root=document_root,
#         show_indexes=show_indexes)

#     response['Access-Control-Allow-Origin'] = '*'
#     return response
