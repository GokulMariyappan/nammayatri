document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map
    var map = L.map('map').setView([12.9716, 77.5946], 12); // Default: Bangalore
    
    // Load OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Pickup and Drop-off Markers (Initially hidden)
    var pickupMarker = null;
    var dropoffMarker = null;
    var routingControl = null;

    // Handle map click to set Pickup & Drop-off
    map.on('click', function(e) {
        if (!pickupMarker) {
            // Set pickup point
            pickupMarker = L.marker(e.latlng, { draggable: true }).addTo(map)
                .bindPopup("📍 Pickup Location").openPopup();
            document.getElementById('from').value = `Lat: ${e.latlng.lat}, Lng: ${e.latlng.lng}`;
            
            // Event listener for dragging
            pickupMarker.on('dragend', function() {
                document.getElementById('from').value = `Lat: ${pickupMarker.getLatLng().lat}, Lng: ${pickupMarker.getLatLng().lng}`;
                drawRoute(); // Update route
            });
        } else if (!dropoffMarker) {
            // Set drop-off point
            dropoffMarker = L.marker(e.latlng, { draggable: true }).addTo(map)
                .bindPopup("📍 Drop-off Location").openPopup();
            document.getElementById('to').value = `Lat: ${e.latlng.lat}, Lng: ${e.latlng.lng}`;

            // Event listener for dragging
            dropoffMarker.on('dragend', function() {
                document.getElementById('to').value = `Lat: ${dropoffMarker.getLatLng().lat}, Lng: ${dropoffMarker.getLatLng().lng}`;
                drawRoute(); // Update route
            });

            // Draw route automatically
            drawRoute();
        }
    });

    // Function to draw shortest route
    function drawRoute() {
        if (pickupMarker && dropoffMarker) {
            // Remove existing route
            if (routingControl) {
                map.removeControl(routingControl);
            }

            // Draw new route using Leaflet Routing Machine
            routingControl = L.Routing.control({
                waypoints: [
                    pickupMarker.getLatLng(),
                    dropoffMarker.getLatLng()
                ],
                routeWhileDragging: false,
                createMarker: function() { return null; }, // Hide default route markers
                lineOptions: {
                    styles: [{ color: 'blue', weight: 6 }] // ✅ Blue route with thickness
                }
            }).addTo(map);
        }
    }

    // Book Now Button Click
    document.querySelector(".book-now").addEventListener("click", function() {
        if (!pickupMarker || !dropoffMarker) {
            alert("❌ Please select both Pickup and Drop-off locations.");
            return;
        }

        alert(`✅ Ride booked!\n📍 Pickup: ${document.getElementById('from').value}\n📍 Drop-off: ${document.getElementById('to').value}`);
    });
});


const socket = new WebSocket('ws://localhost:8000/ws/rides/');

socket.onopen = () => console.log("WebSocket Connected!");
socket.onerror = (error) => console.log("WebSocket Error:", error);
let userRole = null;  // Track if user is a customer or driver

// WebSocket - Listen for real-time ride updates
socket.onmessage = function(event) {
    console.log("WebSocket Message Received:", event.data);
    const data = JSON.parse(event.data);

    // Check if it's a ride request
    if (data.message && data.message.includes("New ride request")) {
        alert(data.message);
        fetchAvailableRides(); // Automatically refresh the ride list
    } else if (data.message && data.message.includes("Your ride has been accepted")) {
        alert(data.message); // Notify the customer about ride acceptance
    }
};

// Login User
function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    console.log(email, password);

    fetch('http://localhost:8000/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('Login successful!');
            localStorage.setItem('user', JSON.stringify(data.user));

            const user = data.user;
            if (user && user.role) {
                userRole = user.role; // Track user role globally
                window.location.href = user.role === 'customer' ? "customer.html" : "driver.html";
            } else {
                console.error("User role missing:", user);
                alert("Error: User role not found.");
            }
        }
    });
}

// Request a Ride
function requestRide() {
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    const user = JSON.parse(localStorage.getItem('user'));

    fetch('http://localhost:8000/request-ride/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_location: from, to_location: to, user: user })
    })
    .then(response => response.json())
    .then(data => {
        alert('Ride Requested!');

        // 🔥 Immediately notify drivers (via WebSocket)
        socket.send(JSON.stringify({ type: "new_ride", message: "New ride available!" }));
    });
}

// Fetch Available Rides for Drivers
function fetchAvailableRides() {
    console.log('Fetching available rides...');
    const user = JSON.parse(localStorage.getItem('user'));

    fetch('http://localhost:8000/available-rides/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user })
    })
    .then(response => response.json())
    .then(data => {
        const rideList = document.getElementById('ride-list');
        rideList.innerHTML = '';

        if (!data.available_rides || data.available_rides.length === 0) {
            rideList.innerHTML = "<li>No rides available</li>";
            return;
        }

        data.available_rides.forEach(ride => {
            const li = document.createElement('li');
            li.innerHTML = `From: ${ride.from_location} - To: ${ride.to_location}
                <button onclick="acceptRide(${ride.id})">Accept</button>`;
            rideList.appendChild(li);
        });
    });
}

// Accept a Ride
function acceptRide(rideId) {
    const user = JSON.parse(localStorage.getItem('user'));

    fetch(`http://localhost:8000/accept-ride/${rideId}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user })
    })
    .then(response => response.json())
    .then(data => {
        alert('Ride Accepted!');
        fetchAvailableRides();
    });
}

// Register a new user
function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const role = document.getElementById('register-role').value;

    fetch('http://localhost:8000/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, role })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('Registration successful! You can now log in.');
        }
    });
}
