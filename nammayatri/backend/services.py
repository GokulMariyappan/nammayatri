import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import RideRequest, CustomUser
from channels.layers import get_channel_layer  # type:ignore
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt

def calculate_distance(from_location, to_location):
    """Simple mock function for distance calculation (Replace with Google Maps API if needed)"""
    return 5.0  # Fixed 5 km for now

@csrf_exempt
def request_ride(request):
    """Handles ride request creation and WebSocket notification"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        from_location = data.get("from_location")
        to_location = data.get("to_location")
        ruser = data.get("user")

        if not from_location or not to_location:
            return JsonResponse({"error": "Missing location details"}, status=400)

        user = get_object_or_404(CustomUser, email=ruser["email"])

        # Calculate price (basic example)
        distance = calculate_distance(from_location, to_location)
        price = distance * 10  

        # Create ride request
        ride = RideRequest.objects.create(customer=user, from_location=from_location, to_location=to_location, price=price)

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

            # Notify the customer via WebSockets
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"customer_{ride.customer.id}",
                {
                    "type": "ride_update",
                    "message": f"Your ride has been accepted by {user.email}!",
                }
            )

            return JsonResponse({"message": "Ride accepted successfully"})
        except RideRequest.DoesNotExist:
            return JsonResponse({"error": "Ride not found or already accepted"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
