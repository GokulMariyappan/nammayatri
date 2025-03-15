const socket = new WebSocket('ws://localhost:8000/ws/rides/');
socket.onopen = () => console.log("WebSocket Connected!");
socket.onerror = (error) => console.log("WebSocket Error:", error);
let userRole = null;  // To track if user is a customer or driver

// WebSocket - Listen for real-time ride updates
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    alert(data.message);  // Notify user when a new ride is requested
};

// Login User
function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

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
            getUserRole(email);
        }
    });
}

// Get User Role
function getUserRole(email) {
    fetch(`http://localhost:8000/get-user-role/?email=${email}`)
    .then(response => response.json())
    .then(data => {
        userRole = data.role;
        if (userRole === 'customer') {
            document.getElementById('customer-section').style.display = 'block';
        } else if (userRole === 'driver') {
            document.getElementById('driver-section').style.display = 'block';
            fetchAvailableRides();
        }
    });
}

// Request a Ride
function requestRide() {
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;

    fetch('http://localhost:8000/request-ride/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_location: from, to_location: to })
    })
    .then(response => response.json())
    .then(data => {
        alert('Ride Requested!');
    });
}

// Fetch Available Rides for Drivers
function fetchAvailableRides() {
    fetch('http://localhost:8000/available-rides/')
    .then(response => response.json())
    .then(data => {
        const rideList = document.getElementById('ride-list');
        rideList.innerHTML = '';
        data.rides.forEach(ride => {
            const li = document.createElement('li');
            li.innerHTML = `From: ${ride.from_location} - To: ${ride.to_location}
                <button onclick="acceptRide(${ride.id})">Accept</button>`;
            rideList.appendChild(li);
        });
    });
}

// Accept a Ride
function acceptRide(rideId) {
    fetch(`http://localhost:8000/accept-ride/${rideId}/`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        alert('Ride Accepted!');
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
