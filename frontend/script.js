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
            console.log(localStorage.getItem('user'));
                if(data.user.role === 'customer') window.location.href = "customer.html";
                else {
                    window.location.href = "driver.html";
                }
        }
    });
}

// Get User Role
function getUserRole(email) {
    fetch(`http://localhost:8000/get-user-role/${email}`)
    .then(response => response.json())
    .then(data => {
        userRole = data.role;
        if (userRole === 'customer') {
            document.getElementById('customer-section').style.display = 'block';
        } else if (userRole === 'driver') {
            document.getElementById('driver-section').style.display = 'block';
           
        }
    });
}

// Request a Ride
function requestRide() {
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    console.log(JSON.parse(localStorage.getItem('user')));
    const user = JSON.parse(localStorage.getItem('user'));
    fetch('http://localhost:8000/request-ride/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_location: from, to_location: to, user : user })
    })
    .then(response => response.json())
    .then(data => {
        alert('Ride Requested!');
    });
}

// Fetch Available Rides for Drivers
function fetchAvailableRides() {
    console.log('this fucntion is called');
    const user = localStorage.getItem('user');
    fetch('http://localhost:8000/available-rides/',{
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user : user })
    })
    .then(response => response.json())
    .then(data => {
        const rideList = document.getElementById('ride-list');
        rideList.innerHTML = '';
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
    const user = localStorage.getItem('user');
    fetch(`http://localhost:8000/accept-ride/${rideId}/`, { method: 'POST', body : JSON.stringify({user : user})  })
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
