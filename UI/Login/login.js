// login.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const cnp = document.getElementById('cnp').value.trim();
        const nume = document.getElementById('nume').value.trim();
        const prenume = document.getElementById('prenume').value.trim();

        // Simple validation
        if (!cnp || !nume || !prenume) {
            alert('Te rugăm să completezi toate câmpurile!');
            return;
        }

        // Example: show the entered data (replace with real authentication logic)
        alert(`CNP: ${cnp}\nNume: ${nume}\nPrenume: ${prenume}`);

        // You can add AJAX/fetch here to send data to backend
    });
});

