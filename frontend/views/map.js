var Backbone = require('backbone'),
    template = require("../templates/map.hbs"),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client');


var query = "";
hashtrack.onhashvarchange('q', function(_, value) {
    query = value;
    $('#page').trigger('search', value)
})
hashtrack.onhashvarchange('t', function(_, value) {
    query = value;
    $('#page').trigger('search', value)
})

module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this;
        this.query = query;
        this.services = new service.PublicServices();
        this.servicetypes = new servicetype.ServiceTypes();
        this.render();
    },

    render: function() {
        var $el = this.$el;
        var self=this;
        this.$el.html(template({
            services: this.services,
            query: this.query,
        }));

        this.servicetypes.fetch().then(function() {
            var $select = $('.query-service-type');
            $.each(self.servicetypes.models, function() {
                var d = this.data();
                $select.append('<option value="'+d.number +'">'+d.name+'</option>')
            })
            var t = hashtrack.getVar('t');
            if (t) {
                $select.val(t);
            }
        });

        function initialize() {
            var mapOptions = {
                center: { lat: -34.397, lng: 150.644},
                zoom: 8
            };
            self.map = new google.maps.Map(document.getElementById('map_canvas'),
                mapOptions);
            self.refetchServices(self.query);
        }

        initialize();
    },

    updateMarkers: function() {
        var self = this;
        var bounds = new google.maps.LatLngBounds();
        var services = this.services.data();
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
                marker.setMap(self.map);
                google.maps.event.addListener(marker, 'click', function() {
                    location.hash = '#/services/' + service.id + '/';
                })
            }
        });
        self.map.fitBounds(bounds);
    },

    refetchServices: function() {
        var self = this;
        this.query = hashtrack.getVar('q');
        this.type = hashtrack.getVar('t');
        var params = {
            search: self.query,
            type_numbers: this.type,
        };
        this.services.fetch({data: params}).then(function(){
            self.updateMarkers();
        })
    },

    events: {
        "search": function(_, query) {
            this.refetchServices();
        },
        "input input.query": function(e) {
            var query = $(e.target).val();
            // this.refetchServices(query);
            hashtrack.setVar('q', query);
        },
        "change .query-service-type": function(e) {
            hashtrack.setVar('t', $(e.target).val());
        },
    }
})
