var Backbone = require('backbone'),
    template = require("../templates/map.hbs"),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client'),
    search = require('../search')
;


module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this;
        this.query = "";
        this.services = new service.PublicServices();
        this.servicetypes = new servicetype.ServiceTypes();
        //this.render();
        this.markers = [];
    },

    render: function() {
        var $el = this.$el;

        var self=this;
        this.$el.html(template({
            services: this.services,
            query: hashtrack.getVar('q'),
        }));
        $('.no-search-results').hide();

        var $scv = this.$el.find('#search_controls');
        var SearchControlView = new search.SearchControls({
            $el: $scv,
        });
        SearchControlView.render();

        function initialize() {
            var mapOptions = {
                center: { lat: 33.8869, lng: 35.5131},
                zoom: 8
            };
            self.map = new google.maps.Map(document.getElementById('map_canvas'),
                mapOptions);
            search.refetchServices(self.query).then(function(){
                self.updateResults();
            });
        }

        initialize();
    },

    updateResults: function() {
        var self = this;
        $.each(self.markers, function() {
            this.setMap(null);
        });
        self.markers = [];
        var bounds = new google.maps.LatLngBounds();
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
            // Google Maps API's LatLng() constructor expects LAT, LONG parameters
            var long_lat_str = /(-?\d+\.\d+) (-?\d+\.\d+)/.exec(this.location);
            if (long_lat_str) {
                var myLatlng = new google.maps.LatLng(long_lat_str[2], long_lat_str[1]);
                bounds.extend(myLatlng);
                var marker = new google.maps.Marker({
                    position: myLatlng,
                    title: this.name,
                    icon: new google.maps.MarkerImage(
                        this.servicetype.icon_url,
                        null,
                        null,
                        new google.maps.Point(12, 12),
                        new google.maps.Size(24, 24)
                    ),
                });
                window.marker = marker;
                marker.setMap(self.map);
                self.markers.push(marker);
                google.maps.event.addListener(marker, 'click', function() {
                    location.hash = '#/service/' + service.id;
                })
            }
        });
        self.map.fitBounds(bounds);
        var zoom = self.map.getZoom();
        if (zoom > 10) {
            self.map.setZoom(10);
        }
    },

    events: {
        "search": function(_, query) {
            $('.spinner').show();
            var self = this;
            search.refetchServices().then(function(){
                self.updateResults();
                $('.spinner').hide();
            })
        },
        "input input.query": function(e) {
            var query = $(e.target).val();
            hashtrack.setVar('q', query);
        },
        "change .query-service-type": function(e) {
            hashtrack.setVar('t', $(e.target).val());
        },
        "input keyup": function(e) {
            if (e.keyCode === 13) {
                return false;
            }
        },
    }
})
