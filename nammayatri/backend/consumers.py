import json
from channels.generic.websocket import AsyncWebsocketConsumer #type:ignore

class RideConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "ride_requests"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'request_ride':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "new_ride",
                    "message": f"New ride request from {data.get('customer_email')}!"
                }
            )

    async def new_ride(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
