const COORD_PRECISION = 5
const INITIAL_ZOOM = 16;
const MAX_ZOOM = 20;
const SEARCH_RADIUS = 100;
const UNNAMED_ROAD_STRING = "Unnamed"
const IQ_TOKEN = "pk.e27e659d87b04fd8f55014c2e2e82ccc" // locationIQ API token

// Holds all global variables (except constants)
var myPage = Object();

// Create document objects / variables once DOM is loaded
addEventListener("DOMContentLoaded", (event) => {
    myPage.conditionDisplay = document.getElementById('condition-display');
    myPage.coordinateDisplay = document.getElementById('coordinate-display');
    myPage.searchButton = document.getElementById('search-button');
    myPage.map = null;
    myPage.markerLayer = null;
    myPage.selectedCoords = L.latLng(0,0);
    myPage.icon = null;
});

// When search button is clicked
function searchForConditions(ev) {
    console.log("Beginning search for coordinates: " + myPage.selectedCoords.lat.toFixed(COORD_PRECISION) + ", " + myPage.selectedCoords.lng.toFixed(COORD_PRECISION))
    
    // Format for LocationIQ API call - LONGITUDE BEFORE LATITUDE
    var url = "https://us1.locationiq.com/v1/nearest/driving/"
        + myPage.selectedCoords.lng.toFixed(7) + ","
        + myPage.selectedCoords.lat.toFixed(7) + "?radiuses="
        + SEARCH_RADIUS + "&key="
        + IQ_TOKEN
        + "&number=1"; 

    // Make call
    fetch(url)
    .then((response) => {
        console.log("URL fetched");
        if (!response.ok) {
            throw new Error(`HTTP error. Status: ${response.status}`);
        }
        // get response as JSON
        return response.json();
    })
    .then(resp => {
        console.log(resp);

        // some small local roads do not have a name
        var roadName = (resp.waypoints[0].name != "") ? resp.waypoints[0].name : UNNAMED_ROAD_STRING;

        // call roadMonitor API to receive our IRI back
    
        // format results for HTML
        var conditionResults = '<span class="main-accent">Road: </span>' + roadName;

        // display results to user
        myPage.conditionDisplay.innerHTML = conditionResults;
    }).catch((error) => {
        console.log(error);

        // tell the user to select a point closer to their desired road
        var errorMsg = '<span class="main-accent">Sorry, no nearby road found.</span><br>Please select coordinates that are closer to the desired road.';
        myPage.conditionDisplay.innerHTML = errorMsg;
    });
}

// Runs after map is fully initialized - sets up all other variables and events for the search functionality
function initializePage() {
    displayCoordinates(myPage.selectedCoords, myPage.coordinateDisplay);

    myPage.icon = L.icon({
        iconUrl: '../images/mapMarker.png',
        iconSize: [50, 56],
        iconAnchor: [25, 47],
        shadowUrl: '../images/mapMarkerShadow.png',
        shadowSize: [50, 56],
        shadowAnchor: [25, 47]
    });
    myPage.markerLayer = L.marker(myPage.selectedCoords, {icon: myPage.icon}).addTo(myPage.map);

    // Update selected coordinates on map click
    myPage.map.on('click', function(ev) {
        console.log("Map clicked, setting new coordinates");
        myPage.selectedCoords = myPage.map.mouseEventToLatLng(ev.originalEvent);
        displayCoordinates(myPage.selectedCoords, myPage.coordinateDisplay);

        // delete old marker and add new one 
        myPage.markerLayer.remove();
        myPage.markerLayer = L.marker(myPage.selectedCoords, {icon: myPage.icon}).addTo(myPage.map);
    });

    // Search and display on search button press
    myPage.searchButton.addEventListener('click', searchForConditions);
}

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
    myPage.map = L.map('map').setView([position.coords.latitude, position.coords.longitude], INITIAL_ZOOM);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: MAX_ZOOM,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(myPage.map);

    console.log("Map initialized to current location");
    initializePage();
}

// Place the map in the fallback position (center of Ottawa)
function initializeMapFailure() {
    myPage.map = L.map('map').setView([45.4201, 75.7003], INITIAL_ZOOM);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: MAX_ZOOM,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(myPage.map);

    console.log("Map initialized to default position");
    initializePage();
}

function displayCoordinates(coords, coordinateDisplay) {
    coordinateDisplay.innerHTML = "Selected Coordinates:<br>" + coords.lat.toFixed(COORD_PRECISION) + ", " + coords.lng.toFixed(COORD_PRECISION);
}

function displayConditions(coords, conditionDisplay) {

}

/* ==== MAIN ==== */
initializeMap();

