from channels import Group
from channels.sessions import channel_session
from .models import Room
import json

@channel_session
def ws_connect(message):
   print("Connected")

@channel_session
def ws_receive(message):
   print("received")

@channel_session
def ws_disconnect(message):
    print("disconneted")
