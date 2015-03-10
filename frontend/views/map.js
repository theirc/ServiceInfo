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
        this.render();
    },

    render: function() {
        var $el = this.$el;
        var self=this;
        this.$el.html(template({
            services: this.services,
            query: hashtrack.getVar('q'),
        }));

        search.populateServiceTypeDropdown();

        function initialize() {
            var mapOptions = {
                center: { lat: 33.8869, lng: 35.5131},
                zoom: 8
            };
            self.map = new google.maps.Map(document.getElementById('map_canvas'),
                mapOptions);
            search.refetchServices(self.query).then(function(){
                self.updateMarkers();
            });
        }

        initialize();
    },

    updateMarkers: function() {
        var self = this;
        var bounds = new google.maps.LatLngBounds();
        var services = search.services.data();
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
                });
                marker.setMap(self.map);
                google.maps.event.addListener(marker, 'click', function() {
                    location.hash = '#/services/' + service.id + '/';
                })
            }
        });
        self.map.fitBounds(bounds);
    },

    events: {
        "search": function(_, query) {
            var self = this;
            search.refetchServices().then(function(){
                self.updateMarkers();
            })
        },
        "input input.query": function(e) {
            var query = $(e.target).val();
            hashtrack.setVar('q', query);
        },
        "change .query-service-type": function(e) {
            hashtrack.setVar('t', $(e.target).val());
        },
    }
})
