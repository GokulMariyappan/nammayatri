import json
from channels.generic.websocket import AsyncWebsocketConsumer  # type:ignore

class RideConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")  # Get authenticated user
        self.group_name = None

        if self.user and self.user.is_authenticated:
            if self.user.role == "driver":
                self.group_name = "drivers_group"  # Drivers receive ride requests
            else:
                self.group_name = f"customer_{self.user.id}"  # Customers get their ride updates
            
            await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages from WebSocket clients"""
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'request_ride':
            await self.channel_layer.group_send(
                "drivers_group",  # Send only to drivers
                {
                    "type": "new_ride",
                    "message": f"New ride request from {data.get('customer_email')}!",
                }
            )

    async def new_ride(self, event):
        """Sends ride request notification to drivers"""
        await self.send(text_data=json.dumps({"message": event["message"]}))

    async def ride_update(self, event):
        """Sends ride status updates to customers"""
        await self.send(text_data=json.dumps({"message": event["message"]}))
