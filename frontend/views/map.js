var Backbone = require('backbone'),
    config = require('../config'),
    template = require("../templates/map.hbs"),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    i18n = require('i18next-client'),
    search = require('../search')
;

// required here because this is the only view that needs it
require('marker-spider/dist/oms.min');


module.exports = Backbone.View.extend({
    feedback: false,
    // Start map centered on Beirut each time it's loaded
    map_center: {lat: 33.8869, lng: 35.5131},

    initialize: function(params){
        var self = this;
        this.feedback = params.hasOwnProperty('feedback');
        this.markers = [];
    },

    perform_query: function() {
        var self = this;
        // Always center queries from the map view on the current center of the map
        search.refetchServices(self.map_center).then(function() {
            self.renderResults();
        });
    },

    render: function() {
        var $el = this.$el,
            self = this;

        this.$el.html(template({
            feedback: this.feedback
        }));
        $('.no-search-results').hide();
        $('.results-truncated').hide();

        // Renders automatically when language is ready
        this.SearchControlView = new search.SearchControls({
            $el: this.$el.find('#search_controls'),
            feedback: this.feedback
        });
        this.SearchControlView.on('search_parameters_changed', this.perform_query, this);

        var mapOptions = {
            // Center the map wherever it was last time
            center: this.map_center,
            // Zoom level to see most of Lebanon
            zoom: 8
        };
        this.map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);

        this.spiderfier = new OverlappingMarkerSpiderfier(self.map);
        this.spiderfier.addListener('click', function(marker, event) {
            // User clicks on a limb of the spider. Go to that service
            location.hash = '#/service/' + marker.serviceId;
        });
        google.maps.event.addListener(this.map, 'bounds_changed', function() {
            self.bounds_changed();
        });
        google.maps.event.addListener(this.map, 'center_changed', function() {
            var center = self.map.getCenter();
            self.center_changed({lat: center.lat(), lng: center.lng()});
        });

        this.perform_query();
    },

    bounds_changed: function() {
        // We call this when the user moves the bounds of the map.  If they drag, we'll
        // get called a ton of times, so we don't actually do anything until we go a bit without
        // any new updates.
        if (this.bounds_timeout) {
            clearTimeout(this.bounds_timeout);
        }
        var self = this;
        this.bounds_timeout = setTimeout(function () {
            // Don't need to repeat search, just show results on different sized map
            // so we can update the "NN services shown" message correctly.
            if (search.services.data().length) {
                self.renderResults();
            }
        }, 500);
    },

    center_changed: function(new_latlon) {
        // We call this when the user moves the center of the map.  If they drag, we'll
        // get called a ton of times, so we don't actually do anything until we go a bit without
        // any new updates.
        this.map_center = new_latlon;
        if (this.timeout) {
            clearTimeout(this.timeout);
        }
        var self = this;
        this.timeout = setTimeout(function () {
            self.perform_query();
        }, 500);
    },

    renderResults: function() {
        var self = this,
            msg = '',
            map_bounds = this.map.getBounds(),
            num_visible_markers = 0;
        $.each(self.markers, function() {
            this.setMap(null);  // yes this should be 'this'
        });
        self.spiderfier.clearMarkers();
        self.markers = [];
        var services = search.services.data();
        if (services.length === 0) {
            $('.no-search-results').show();
            $('#map_container').hide();
            return;
        }
        $('.no-search-results').hide();
        $('#map_container').show();


        $.each(services, function() {
            var service = this;

            // this.location, from PostGIS, is in the form POINT(LONG LAT)
            // Google Maps API's LatLng() constructor expects LAT, LNG parameters
            var long_lat_str = /(-?\d+\.\d+) (-?\d+\.\d+)/.exec(service.location);
            if (long_lat_str) {
                var myLatlng = new google.maps.LatLng(long_lat_str[2], long_lat_str[1], true);
                if (map_bounds.contains(myLatlng)) {
                    num_visible_markers += 1;
                    var marker = new google.maps.Marker({
                        position: myLatlng,
                        title: this.name,
                        icon: new google.maps.MarkerImage(
                            this.servicetype.icon_url,
                            null,
                            null,
                            new google.maps.Point(12, 12),
                            new google.maps.Size(24, 24)
                        )
                    });
                    window.marker = marker;
                    marker.setMap(self.map);
                    marker.serviceId = service.id;
                    self.spiderfier.addMarker(marker);
                    self.markers.push(marker);
                }
            }
        });
        if (num_visible_markers < search.total_results) {
            msg = i18n.t("Service-Map.More-Results", {
                // I'd like to call the next variable "count", but "count" is a
                // magic var name to i18n and won't work here, because i18n.t
                // mingles its options and its variable values.
                // "thecount" sounds stupid, but it works.
                thecount: num_visible_markers,
                total_results: search.total_results,
                interpolationPrefix: '{',
                interpolationSuffix: '}'
            });
        }
        $('span#more_results').text(msg);
    }
});
