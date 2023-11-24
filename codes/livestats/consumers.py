# # livestats/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import RoomStats

# class LiveStatsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f"live_stats_{self.room_name}"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#         await self.update_members_count()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.update_members_count()

#     async def receive(self, text_data):
#         # Handle received messages if needed

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat.message',
#                 'message': text_data,
#             }
#         )

#         await self.update_members_count()

#     async def chat_message(self, event):
#         await self.send(text_data=event['message'])

#     async def update_members_count(self):
#         members_count = RoomStats.objects.filter(room_name=self.room_name).count()

#         await self.send(text_data=json.dumps({
#             'members_count': members_count,
#         }))
