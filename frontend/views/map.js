var Backbone = require('backbone'),
    template = require("../templates/map.hbs"),
    models = require('../models/service'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client');


var query = "";
hashtrack.onhashvarchange('q', function(_, value) {
    query = value;
    $('#page').trigger('search', value)
})

module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this;
        this.query = query;
        this.services = new models.PublicServices();
        this.services.fetch({data: {name: query}}).then(function(){
            self.render();
        })
    },

    render: function() {
        var $el = this.$el;
        var map;
        this.$el.html(template({
            services: this.services,
        }));

        var services = this.services.data();
        function initialize() {
            var mapOptions = {
                center: { lat: -34.397, lng: 150.644},
                zoom: 8
            };
            map = new google.maps.Map(document.getElementById('map_canvas'),
                mapOptions);
            var bounds = new google.maps.LatLngBounds();

            $.each(services, function() {
                var service = this;
                var latlng_string = /(\d+\.\d+) (\d+\.\d+)/.exec(this.location);
                if (latlng_string) {
                    var myLatlng = new google.maps.LatLng(latlng_string[1], latlng_string[2]);
                    bounds.extend(myLatlng);
                    var marker = new google.maps.Marker({
                        position: myLatlng,
                        title: this.name,
                    });
                    marker.setMap(map);
                    google.maps.event.addListener(marker, 'click', function() {
                        location.hash = '#/services/' + service.id + '/';
                    })
                }
            });

            map.fitBounds(bounds);
        }

        initialize();
    },

    events: {
        "search": function(_, query) {
            this.query = query;
            var self = this;
            this.services.fetch({data: {name: query}}).then(function(){
                self.render();
            })
        }
    }
})
