import json
import asyncio
from channels.generic.websocket import JsonWebsocketConsumer
from channels.db import database_sync_to_async
from tasks.models import ChatRoom, ApiKey, Agent
from django.http import HttpResponse
from channels.consumer import SyncConsumer
class ChatConsumer(SyncConsumer):
   def websocket_connect(self,event):
      print('connect event called ')
   def websocket_receive(self,event):
      print("new event is recive")
      print(event)