
// Approximately the middle of Luxembourg when looking on the map
let LUX_CENTER_POS = [49.8142371307, 6.098083879];

var lateness_total = true;
var lateness_average = false;
var stops_mode = stops;

var lateness_1_max = 3;
var lateness_2_max = 6;
var lateness_3_max = 10;


var map = L.map("map").setView(LUX_CENTER_POS, 10);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
                //attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                maxZoom: 18,
                minZoom: 1,
                zoomControl: true,
                id: 'mapbox/streets-v11',
                tileSize: 512,
                zoomOffset: -1,
                accessToken: 'pk.eyJ1IjoiM3FoNCIsImEiOiJja3NqYW53NXQxc2l2Mm5vZmF0cGVydnYxIn0.TF0GeHY58O9gdLTT88Sb0g'
            }).addTo(map);


// update values for lateness when changed by user //
function update_lateness_all() {
  lateness_1_max = document.getElementById('change_late_1').value;
  document.getElementById('change_late_1_text').innerHTML = '0-' + lateness_1_max;

  lateness_2_max = document.getElementById('change_late_2').value;
  document.getElementById('change_late_2_text').innerHTML = lateness_1_max + '-' + lateness_2_max;

  lateness_3_max = document.getElementById('change_late_3').value;
  document.getElementById('change_late_3_text').innerHTML = lateness_2_max + '-' + lateness_3_max;
}
// Reset values for lateness //
document.getElementById('reset').onclick = function() {
  document.getElementById('change_late_1').value = 3;
  document.getElementById('change_late_1_text').innerHTML = "0-3";
  lateness_1_max = 3;
  document.getElementById('change_late_2').value = 6;
  document.getElementById('change_late_2_text').innerHTML = "3-6";
  lateness_2_max = 6;
  document.getElementById('change_late_3').value = 10;
  document.getElementById('change_late_3_text').innerHTML = "6-10";
  lateness_3_max = 10;
}

// -----------------------------------------//
// Get user location to center map on user //
function getLocation() {
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(get_position, showError);
  }
  else {
      reject("Unknown error happened while trying to access location data from user.");
  }
}

function get_position(position) {
  if (!(LUX_CENTER_POS == [49.8142371307, 6.098083879]) & (LUX_CENTER_POS == null)) {
      var LUX_CENTER_POS = [position.coords.latitude, position.coords.longitude];
      map.panTo(new L.LatLng(position.coords.latitude, position.coords.longitude));
      console.log(LUX_CENTER_POS);
  }
  
}
function showError(error) {
  switch(error.code) {
      case error.PERMISSION_DENIED:
          console.log("User denied access to location.");
          break;
      case error.POSITION_UNAVAILABLE:
          console.log("Location information not available.");
          break;
      case error.TIMEOUT:
          console.log("The location request timed out.");
          break;
      case error.UNKNOWN_ERROR:
          console.log("Unknown error.");
          break;
  }
}
getLocation();
// -----------------------------------------//


// ----------------------------------------//
//              Marker colors             //

var marker_default = {
    radius: 5,
    fillColor: "#000000",
    color: "#000000", //black
    weight: 1,
    opacity: 1,
    fillOpacity: 1,
};

var marker_late_1 = {
  radius: 5,
  fillColor: "#21b824", //green
  color: "#000000",
  weight: 1,
  opacity: 0.1,
  fillOpacity: 0.8,
}

var marker_late_2 = {
  radius: 5,
  fillColor: "#ffff00", //yellow
  color: "#000000",
  weight: 1,
  opacity: 0.4,
  fillOpacity: 0.8,
}

var marker_late_3 = {
  radius: 5,
  fillColor: "#f28816", //orange
  color: "#000000",
  weight: 1,
  opacity: 0.4,
  fillOpacity: 0.8,
}

var marker_late_4 = {
  radius: 5,
  fillColor: "#ff0000", //red
  color: "#000000",
  weight: 2,
  opacity: 1,
  fillOpacity: 0.8
}

var marker_error = {
  icon: L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    className: 'blinking' // Look at CSS that makes it blink
  })
}
// ----------------------------------- //

var intervalId = window.setInterval(function(){
  update_markers()
}, 2000); //equals 30 seconds


// Marker groups
var markers_green = new L.layerGroup();
var markers_yellow = new L.layerGroup();
var markers_orange = new L.layerGroup();
var markers_red = new L.layerGroup();
var markers_others = new L.layerGroup();

var show_green = true;
var show_yellow = true;
var show_orange = true;
var show_red = true;
var show_others = true;


function update_markers() {
  if (lateness_total == true || lateness_average == false) {
    stops_mode = stops;
  }
  else if (lateness_average == true || lateness_total == false) {
    stops_mode = stops_average;
  }

  try {
    markers_green.clearLayers();
    markers_yellow.clearLayers();
    markers_orange.clearLayers();
    markers_red.clearLayers();
    markers_others.clearLayers();
    console.log("Deleted markers");
  }
  catch(err) {
    console.log("Unable to delete markers!")
  };

  

  L.geoJSON(stops_mode, {
    onEachFeature: onEachFeature,
    pointToLayer: function (feature, latlng) {
      //console.log(feature.properties.late)

      if (feature.properties.late <= lateness_1_max) {
        var marker = L.circleMarker(latlng, marker_late_1).addTo(markers_green);
      }
      else if (feature.properties.late > lateness_1_max && feature.properties.late <= lateness_2_max) {
        var marker =  L.circleMarker(latlng, marker_late_2).addTo(markers_yellow);
      }
      else if (feature.properties.late > lateness_2_max && feature.properties.late <= lateness_3_max) {
        var marker = L.circleMarker(latlng, marker_late_3).addTo(markers_orange);
      }
      else if (feature.properties.late > lateness_3_max) {
        var marker = L.circleMarker(latlng, marker_late_4)
        markers_red.addLayer(marker);
      }
      else if (feature.properties.late == "ERROR") {
        //var marker = L.marker(latlng, marker_error); //Produces huge lags if lots of Errors
        var marker = L.circleMarker(latlng, marker_default).addTo(markers_others);
      }

      else {
        //var marker = L.circleMarker(latlng, marker_default).addTo(markers_others);
        var marker = L.marker(latlng, marker_error);
      };
      return marker;
    }
  },
  )
  if (show_green == true) {
    markers_green.addTo(map);
  }
  if (show_yellow == true) {
    markers_yellow.addTo(map);
  }
  if (show_orange == true) {
    markers_orange.addTo(map);
  }
  if (show_red == true) {
    markers_red.addTo(map);
  }
  if (show_others == true) {
    markers_others.addTo(map);
  }

};


function onEachFeature(feature, layer) {
  var popupContent = feature.properties.name;

  if (!(feature.properties.late == "ERROR")) {
    layer.bindTooltip("<center>" + popupContent + "<br> Id: " + feature.properties.id + "<br> Late: " + feature.properties.late + " minutes </center>");
  //layer.bindPopup(popupContent);
  }
  else if (feature.properties.late == "ERROR") {
    layer.bindTooltip("<center>" + popupContent + "<br> Id: " + feature.properties.id + "<br> Late: " + feature.properties.late + " minutes </center><br> Coordinates:" + feature.geometry.coordinates);
  }
}


function do_hide_green() {
  if (show_green == true) {
    show_green = false;
    map.removeLayer(markers_green);
  }
  else if (show_green == false) {
    show_green = true;
    markers_green.addTo(map);
  }
}

function do_hide_yellow() {
  if (show_yellow == true) {
    show_yellow = false;
    map.removeLayer(markers_yellow);
  }
  else if (show_yellow == false) {
    show_yellow = true;
    markers_yellow.addTo(map);
  }
}

function do_hide_orange() {
  if (show_orange == true) {
    show_orange = false;
    map.removeLayer(markers_orange);
  }
  else if (show_orange == false) {
    show_orange = true;
    markers_orange.addTo(map);
  }
}

function do_hide_red() {
  if (show_red == true) {
    show_red = false;
    map.removeLayer(markers_red);
  }
  else if (show_red == false) {
    show_red = true;
    markers_red.addTo(map);
  }
}

function do_hide_others() {
  if (show_others == true) {
    show_others = false;
    map.removeLayer(markers_others);
  }
  else if (show_others == false) {
    show_others = true;
    markers_others.addTo(map);
  }
}




