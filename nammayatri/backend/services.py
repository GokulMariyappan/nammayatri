import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import RideRequest, CustomUser, Token
from channels.layers import get_channel_layer  # type:ignore
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import math, re

def calculate_distance(from_location, to_location):
    # Radius of the Earth in kilometers
    R = 6371.0
    match_from = re.match(r"Lat:\s*(-?\d+\.\d+),\s*Lng:\s*(-?\d+\.\d+)", from_location)
    match_to = re.match(r"Lat:\s*(-?\d+\.\d+),\s*Lng:\s*(-?\d+\.\d+)", to_location)
    
    lat1 = float(match_from.group(1))  # Extract latitude and convert to float
    lon1 = float(match_from.group(2))  # Extract longitude and convert to float
    lat2 = float(match_to.group(1)) 
    lon2 = float(match_to.group(2)) 
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance  # Fixed 5 km for now

@csrf_exempt
def request_ride(request):
    """Handles ride request creation and WebSocket notification"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        from_location = data.get("from_location")
        zone = data.get("zone")
        to_location = data.get("to_location")
        worded_from_location = data.get("word_from")
        worded_to_location = data.get('word_to')
        ruser = data.get("user")

        if not from_location or not to_location:
            return JsonResponse({"error": "Missing location details"}, status=400)

        user = get_object_or_404(CustomUser, email=ruser["email"])

        # Calculate price (basic example)
        distance = calculate_distance(from_location, to_location)

        if zone == "red":
            price = distance * 20  + 30
        else:
            price = distance*20 -30

        # Create ride request
        ride = RideRequest.objects.create(customer=user, from_location=from_location, to_location=to_location, worded_from_location = worded_from_location, worded_to_location = worded_to_location, price=price, zone = zone)

        # Notify all drivers via WebSockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "drivers_group",  # Notify only drivers
            {
                "type": "new_ride",
                "message": f"New ride request from {user.email}!",
            }
        )

        return JsonResponse({"message": "Ride requested successfully", "ride_id": ride.id})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

@csrf_exempt
def get_available_rides(request):
    """Retrieves pending ride requests (For drivers)"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        ruser = data.get("user")
        user = get_object_or_404(CustomUser, email=ruser["email"])

        if user.role != "driver":
            return JsonResponse({"error": "Only drivers can see ride requests"}, status=403)

        rides = RideRequest.objects.filter(status="pending").values("id", "customer__email", "from_location", "to_location", "price")
        
        return JsonResponse({"available_rides": list(rides)})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

@csrf_exempt
def accept_ride(request, ride_id):
    """Handles ride acceptance and notifies the customer"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        ruser = data.get("user")
        user = get_object_or_404(CustomUser, email=ruser["email"])

        if user.role != "driver":
            return JsonResponse({"error": "Only drivers can accept rides"}, status=403)

        try:
            ride = RideRequest.objects.get(id=ride_id, status="pending")
            ride.status = "accepted"
            ride.driver = user
            ride.save()

            # if(ride.zone == 'green'):
            #     tokenobj = get_object_or_404(Token,  driver = user)
            #     if(tokenobj.tokens):
            #         if(tokenobj.tokens == 6):
            #             tokenobj.tokens = 0
            #         tokenobj.tokens += 1
            #     tokenobj.tokens = 1

            # Notify the customer via WebSockets
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"customer_{ride.customer.id}",
                {
                    "type": "ride_update",
                    "message": f"Your ride has been accepted by {user.email}!",
                }
            )

            return JsonResponse({"message": "Ride accepted successfully", "from_location" : ride.from_location, "to_location" : ride.to_location})
        except RideRequest.DoesNotExist:
            return JsonResponse({"error": "Ride not found or already accepted"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
