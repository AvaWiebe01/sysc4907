const COORD_PRECISION = 5
const INITIAL_ZOOM = 16;
const MAX_ZOOM = 20;
const UNNAMED_ROAD_STRING = "Unnamed";
const DEFAULT_TIMERANGE_START = "2000-01-01T00:00";
const IQ_SEARCH_RADIUS = 100;
const IQ_TOKEN = "pk.e27e659d87b04fd8f55014c2e2e82ccc"; // locationIQ API token

// Holds all global variables (except constants)
let myPage = Object();

// Create document objects / variables / eventListeners once DOM is loaded
addEventListener("DOMContentLoaded", (event) => {
    myPage.currentDate = new Date();
    myPage.currentDate.setMinutes(myPage.currentDate.getMinutes() - myPage.currentDate.getTimezoneOffset()); // convert to local time
    myPage.currentDate = myPage.currentDate.toISOString().slice(0,-8); // ignore seconds, millis, timezone (UTC)

    // Get references to page elements
    myPage.conditionDisplay = document.getElementById('condition-display');
    myPage.coordinateDisplay = document.getElementById('coordinate-display');
    myPage.radiusDisplay = document.getElementById('radius-display');
    myPage.timerangeStart = document.getElementById('timerange-start');
    myPage.timerangeEnd = document.getElementById('timerange-end');
    myPage.radiusSlider = document.getElementById('radius-slider');
    myPage.searchButton = document.getElementById('search-button');

    // Delcare internal variables for page/search parameters
    myPage.map = null;
    myPage.markerLayer = null;
    myPage.selectedCoords = L.latLng(0,0);
    myPage.selectedRadius = myPage.radiusSlider.value;
    myPage.selectedTimerange = new Array(DEFAULT_TIMERANGE_START, myPage.currentDate);
    myPage.icon = null;

    // Update radius when slider is moved
    myPage.radiusSlider.addEventListener("input", updateSearchRadius);

    // Update timerange when date is selected
    myPage.timerangeStart.addEventListener("input", updateSearchTimerange);
    myPage.timerangeEnd.addEventListener("input", updateSearchTimerange);

});

// When radius slider is moved
function updateSearchRadius(ev) {
    myPage.selectedRadius = myPage.radiusSlider.value;
    myPage.radiusDisplay.innerHTML = "Search Radius:<br>" + myPage.selectedRadius + "m";
    console.log("Radius updated");
}

function updateSearchTimerange(ev) {
    myPage.selectedTimerange[0] = myPage.timerangeStart.value;
    myPage.selectedTimerange[1] = myPage.timerangeEnd.value;
    console.log("Timerange updated")
}

// When search button is clicked
function searchForConditions(ev) {
    console.log("Beginning search for coordinates: " + myPage.selectedCoords.lat.toFixed(COORD_PRECISION) + ", " + myPage.selectedCoords.lng.toFixed(COORD_PRECISION))
    
    // Convert user's local timerange into UNIX epoch
    let epochStart = new Date(myPage.selectedTimerange[0] + "Z");
    epochStart.setMinutes(epochStart.getMinutes() + epochStart.getTimezoneOffset());
    let epochEnd = new Date(myPage.selectedTimerange[1] + "Z");
    epochEnd.setMinutes(epochEnd.getMinutes() + epochEnd.getTimezoneOffset());

    let epochTimerange = new Array(epochStart.getTime(), epochEnd.getTime());
    console.log("Start: " + epochStart.toISOString() + "\nEnd: " + epochEnd.toISOString());

    // Validate selected timerange
    if(epochTimerange[0] >= epochTimerange[1]) {
        // Tell the user that range is invalid
        myPage.conditionDisplay.innerHTML = '<span class="main-accent">Sorry, that time range isn&apos;t allowed.</span><br>Ensure that the end time is after the start time.';
        console.log("Invalid time range");
        return;
    }

    // Format for LocationIQ API call - LONGITUDE BEFORE LATITUDE
    let url = "https://us1.locationiq.com/v1/nearest/driving/"
        + myPage.selectedCoords.lng.toFixed(7) + ","
        + myPage.selectedCoords.lat.toFixed(7) + "?radiuses="
        + IQ_SEARCH_RADIUS + "&key="
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
        let roadName = (resp.waypoints[0].name != "") ? resp.waypoints[0].name : UNNAMED_ROAD_STRING;

        // call roadMonitor API to receive the requested data
    
        // format results for HTML
        let conditionResults = '<span class="main-accent">Road: </span>' + roadName;

        // display results to user
        myPage.conditionDisplay.innerHTML = conditionResults;
    }).catch((error) => {
        console.log(error);

        // tell the user to select a point closer to their desired road
        let errorMsg = '<span class="main-accent">Sorry, no nearby road found.</span><br>Please select coordinates that are closer to the desired road.';
        myPage.conditionDisplay.innerHTML = errorMsg;
    });
}

// Runs after map is fully initialized - sets up displays & all other variables and events for the search functionality
function initializePage() {
    displayCoordinates(myPage.selectedCoords, myPage.coordinateDisplay);
    updateSearchRadius();
    myPage.timerangeStart.value = myPage.selectedTimerange[0];
    myPage.timerangeEnd.value = myPage.selectedTimerange[1];

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

