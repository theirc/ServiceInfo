(function() {
    var map, widget, input, search_input, searchBox;
    var markers = [];

    function initialize() {

        widget = document.getElementById("duckling-map-widget");
        input = widget.querySelectorAll("input")[1];
        search_input = document.getElementById('pac-input');
        searchBox = new google.maps.places.SearchBox(search_input);

        var myLatLng = parse_point();
        var map_canvas = document.getElementById('map_canvas');
        var map_options = {
            center: myLatLng.lat_lng,
            zoom: myLatLng.zoom_level,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        map = new google.maps.Map(map_canvas, map_options);

        google.maps.event.addListener(map, "click", map_click);
        search_input.addEventListener("keypress", stopDefAction, false);
        google.maps.event.addListener(searchBox, 'places_changed', get_places);
        google.maps.event.addListener(map, 'bounds_changed', change_bounds);

        map.controls[google.maps.ControlPosition.TOP_LEFT].push(search_input);

        if (myLatLng.add_marker) {
            // if there is a pre-set point, add marker
            addMarker(myLatLng.lat_lng);
        }
    }

    function get_places() {
        var places = searchBox.getPlaces();

        for (var i = 0, marker; marker = markers[i]; i++) {
            marker.setMap(null);
        }

        // For each place, get the icon, place name, and location.
        markers = [];
        var bounds = new google.maps.LatLngBounds();
        for (var i = 0, place; place = places[i]; i++) {
            // Create a marker for each place.
            var opts = {
                map: map,
                title: place.name,
                position: place.geometry.location
            };
            if (place.icon) {  // some PlaceResults don't seem to have .icon attributes
                opts.icon = {
                    url: place.icon,
                    size: new google.maps.Size(71, 71),
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(17, 34),
                    scaledSize: new google.maps.Size(25, 25)
                };
            }
            var marker = new google.maps.Marker(opts);

            markers.push(marker);

            bounds.extend(place.geometry.location);
        }

        map.fitBounds(bounds);
    };

    // Bias the SearchBox results towards places that are within the bounds of the
    // current map's viewport.
    function change_bounds() {
        var bounds = map.getBounds();
        searchBox.setBounds(bounds);
    };

    // Prevent enter key from submitting entire form
    function stopDefAction(evt) {
        if (evt.keyCode === 13) {
            evt.preventDefault();
        }
    }

    // Draw new marker at click point
    function map_click(event){
        addMarker(event.latLng);
        var point = "POINT (" + event.latLng.lng() + " " + event.latLng.lat() + ")"
        input.value = point;
    }

    // Add a marker to the map and push to the array.
    function addMarker(location) {
        deleteMarkers();

        var marker = new google.maps.Marker({
            position: location,
            map: map
        });
        markers.push(marker);
    }

    function setAllMap(map) {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(map);
        }
    }

    function clearMarkers() {
        setAllMap(null);
    }

    function deleteMarkers() {
        clearMarkers();
        markers = [];
    }

    function parse_point() {
        var value = input.getAttribute("value");
        if (value === "") {
            return {
                lat_lng: new google.maps.LatLng(33.8869, 35.5131),
                zoom_level: 8,
                add_marker: false
            };
        } else {
            var re = /([-\d]\d+\.\d+)\s([-\d]\d+\.\d+)/;
            var point_array = value.match(re);
            return {
                lat_lng: new google.maps.LatLng(point_array[2], point_array[1]),
                zoom_level: 16,
                add_marker: true
            };
        }
    }

    google.maps.event.addDomListener(window, 'load', initialize);
})();
