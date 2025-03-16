var map;
var routingControl;

document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map
    
    map = L.map('map').setView([12.9716, 77.5946], 12); // Default: Bangalore
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    // Pickup and Drop-off Markers (Initially hidden)
    var pickupMarker = null;
    var dropoffMarker = null;
    var routingControl = null;

    function getLocationName(lat, lng, callback) {
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.display_name) {
                    callback(data.display_name);
                } else {
                    callback("Unknown location");
                }
            })
            .catch(() => callback("Error fetching location"));
    }


    // Handle map click to set Pickup & Drop-off
    map.on('click', function(e) {
        if (!pickupMarker) {
            // Set pickup point
            pickupMarker = L.marker(e.latlng, { draggable: true }).addTo(map)
                .bindPopup("📍 Pickup Location").openPopup();
            document.getElementById('from').value = `Lat: ${e.latlng.lat}, Lng: ${e.latlng.lng}`;
            getLocationName(e.latlng.lat, e.latlng.lng, function(address) {
                document.getElementById('word_from').value = address;
            });

            
            // Event listener for dragging
            pickupMarker.on('dragend', function() {
                let newLatLng = pickupMarker.getLatLng();
                getLocationName(newLatLng.lat, newLatLng.lng, function(address) {
                    document.getElementById('word_from').value = address;
                });
                document.getElementById('from').value = `Lat: ${pickupMarker.getLatLng().lat}, Lng: ${pickupMarker.getLatLng().lng}`;
                drawRoute(); // Update route
            });
        } else if (!dropoffMarker) {
            // Set drop-off point
            dropoffMarker = L.marker(e.latlng, { draggable: true }).addTo(map)
                .bindPopup("📍 Drop-off Location").openPopup();
            document.getElementById('to').value = `Lat: ${e.latlng.lat}, Lng: ${e.latlng.lng}`;
            getLocationName(e.latlng.lat, e.latlng.lng, function(address) {
                document.getElementById('word_to').value = address;
            });


            // Event listener for dragging
            dropoffMarker.on('dragend', function() {
                let newLatLng = dropoffMarker.getLatLng();
                document.getElementById('to').value = `Lat: ${dropoffMarker.getLatLng().lat}, Lng: ${dropoffMarker.getLatLng().lng}`;
                getLocationName(newLatLng.lat, newLatLng.lng, function(address) {
                    document.getElementById('word_to').value = address;
                });

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

function extractLocation(address) {
    // Find the position of 'Bengaluru' in the string
    const bengaluruPos = address.indexOf(", Bengaluru");

    if (bengaluruPos !== -1) {
        // Extract the substring before 'Bengaluru'
        const addressBeforeBengaluru = address.slice(0, bengaluruPos).trim();

        // Find the last comma before Bengaluru
        const lastCommaPos = addressBeforeBengaluru.lastIndexOf(",");

        // Extract the string between the last comma and Bengaluru
        const location = addressBeforeBengaluru.slice(lastCommaPos + 1).trim();
        console.log(location);
        return location;
    } else {
        return null; // 'Bengaluru' not found
    }
}

// Request a Ride
async function requestRide() {
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    const word_from = document.getElementById('word_from').value;
    const word_to = document.getElementById('word_to').value;
    const user = JSON.parse(localStorage.getItem('user'));
    let ward = extractLocation(word_from);
            console.log(ward);
    let zone = "normal";
    await fetch('http://localhost:8000/getData/')
        .then(response => response.json())
        .then(data => {
            //first 50 elements
            let arr = Object.keys(data.data);
            let ward = extractLocation(word_from);
            console.log(ward);
            arr.forEach(element => {
                const processedStr1 = element.replace(/\s/g, '').toLowerCase();
                const processedStr2 = ward.replace(/\s/g, '').toLowerCase();
                if(processedStr1 === processedStr2) zone = "red";
            });
            if(zone !== "red") zone = "green";
        }
        );

    fetch('http://localhost:8000/request-ride/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_location: from, to_location: to, user: user, word_from: word_from, word_to : word_to, zone : zone })
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
            li.className = "ride-card";
            li.style = "list-type : none";
            li.innerHTML = `<b>From:</b> ${ride.from_location} - To: ${ride.to_location}
                <button class = "accept-btn" onclick="acceptRide(${ride.id})">Accept</button>`;
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
        alert('Ride Accepted! ' + data.from_location);
        let locationString1 = data.from_location;
        let locationString2 = data.to_location;
        // Extract numbers using regex or split method
        let [lat1, lng1] = locationString1.match(/[-+]?[0-9]*\.?[0-9]+/g).map(Number);
        let [lat2, lng2] = locationString2.match(/[-+]?[0-9]*\.?[0-9]+/g).map(Number);
        // Convert to Leaflet LatLng
        let latLng1 = L.latLng(lat1, lng1);
        let latLng2 = L.latLng(lat2, lng2);


        console.log(latLng1); // Outputs: LatLng(48.72387, 98.49849568)
        console.log(latLng2); 
        fetchAvailableRides();
        initializeMap(latLng1,latLng2);
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


function initializeMap(latLng1, latLng2) {
    // Initialize the map
    console.log(map);
    map.setView(latLng1, 15); // Default: Bangalore
    
    // Load OpenStreetMap tiles
    

    // Pickup and Drop-off Markers (Initially hidden)
    var pickupMarker = L.marker(latLng1, { draggable: true }).addTo(map).bindPopup("📍 Pickup Location").openPopup();
    var dropoffMarker = L.marker(latLng2, { draggable: true }).addTo(map).bindPopup("📍 Drop-off Location").openPopup();
    var routingControl = null;

    drawRoute();

    // Function to draw shortest route
    function drawRoute() {
        if (pickupMarker && dropoffMarker) {
            // Remove existing route

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

        var start = latLng1;
        var destination = latLng2;

        var control = L.Routing.control({
            waypoints: [start, destination],
            routeWhileDragging: false
        }).addTo(map);

        var movingMarker = L.marker(start, { draggable: false }).addTo(map);

        control.on('routesfound', function(e) {
            var route = e.routes[0].coordinates; // Get the route coordinates
            var index = 0; // Start from the first point
            var totalSteps = route.length; // Total points in route
            var interval = 50000 / totalSteps; // Dynamic interval for smooth movement

            function moveMarker() {
                if (index < totalSteps) {
                    movingMarker.setLatLng([route[index].lat, route[index].lng]); // Move marker
                    index++; // Move to the next coordinate
                } else {
                    clearInterval(markerInterval); // Stop when it reaches the destination
                    console.log("joke done");
                }
            }

            // Adjust the interval dynamically for smooth movement
            var markerInterval = setInterval(moveMarker, interval);

        });

    }
}

function showLogin() {
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('register-section').style.display = 'none';

    // Set active button style
    document.getElementById('show-login').classList.add('active');
    document.getElementById('show-register').classList.remove('active');
}

function showRegister() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'block';

    // Set active button style
    document.getElementById('show-login').classList.remove('active');
    document.getElementById('show-register').classList.add('active');
}

function displayHotspotZones(){
    fetch('http://localhost:8000/getData/')
    .then(response => response.json())
    .then(data => {
        const mhlist = document.getElementById('HotSpot');
        mhlist.innerHTML = '';

        places = Object.keys(data.data);
        for(let i = 0; i < 10; i++){
            const li = document.createElement('p');
            li.innerHTML = `${places[i]}`;
            mhlist.appendChild(li);
        }
            
    });
}