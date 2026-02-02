

function initializeMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(initializeMapSuccess, initializeMapFailure)
    }
    else {
        console.log("Geolocation not supported.");
        initializeMapFailure();
    }

    document.getElementById('map').style.zIndex = 0;
}

// Place the map at user's current position
function initializeMapSuccess(position) {
    var map = L.map('map').setView([position.coords.latitude, position.coords.longitude], 16);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    console.log("Map initialized to current location");
}

// Place the map in the fallback position (center of Ottawa)
function initializeMapFailure() {
    var map = L.map('map').setView([45.4201, 75.7003], 16);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    console.log("Map initialized to default position");
}

/* ==== MAIN ==== */

initializeMap();

conditionResults = document.getElementById('condition-display')
