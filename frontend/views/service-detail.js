var Backbone = require('backbone')
,   api = require('../api')
,   template = require("../templates/service-detail.hbs")
,   i18n = require('i18next-client')
,   models = require('../models/models')
,   messages = require('../messages')
;

module.exports = Backbone.View.extend({
    skip_initial_render: true,

    initialize: function(opts){
        var self = this;
        messages.clear();
        var public_services = new models.service.PublicServices();
        this.service = {};

        public_services.fetch({data:{id: opts.id}}).then(function onsuccess(){
            var service = public_services.models[0];
            service.loadSubModels().then(function(){
                self.service = service.data();
                self.render();
            })
        }, function onerror(e) {
            messages.error(e);
        });
    },

    getStaticMap: function(location) {
        /*  https://maps.googleapis.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=13&size=600x300&maptype=roadmap&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318 &markers=color:red%7Clabel:C%7C40.718217,-73.998284
        */

        if (location) {
            var url = "https://maps.googleapis.com/maps/api/staticmap?";
            var long_lat_str = /(-?\d+\.\d+) (-?\d+\.\d+)/.exec(location);
            url = url + "center=" + long_lat_str[2] + "," + long_lat_str[1];
            url = url + "&zoom=16";
            url = url + "&size=640x150";
            url = url + "&markers=color:red%7C" + long_lat_str[2] + "," + long_lat_str[1];

            return url;
        }
    },

    getDirectionsURL: function(service) {
        // The format of the URLs to get a Google directions page appears not to be
        // documented by Google, but people on the net have reverse engineered it.

        // http://gearside.com/easily-link-to-locations-and-directions-using-the-new-google-maps/

        // There are multiple formats that seem to work.  I've chosen this one:
        // https://www.google.com/maps/dir/{{ start addr }}/{{ dest addr }}/@{{ center map on }},{{ zoom level }}z.
        // because other formats didn't seem to center the map on the destination, which was
        // confusing.

        var long_lat_str = /(-?\d+\.\d+) (-?\d+\.\d+)/.exec(service.location),
            latlong = long_lat_str[2] + "," + long_lat_str[1],
            zoom = 16,
            url = "https://www.google.com/maps/dir//" + latlong + "/@" + latlong + "," + zoom + "z";
        return url;
    },

    render: function() {
        var $el = this.$el;
        $el.html(template({
            service: this.service,
            directionsURL: this.getDirectionsURL(this.service),
            mapURL: this.getStaticMap(this.service.location),
            daysofweek: [
                    i18n.t('Global.Sunday'),
                    i18n.t('Global.Monday'),
                    i18n.t('Global.Tuesday'),
                    i18n.t('Global.Wednesday'),
                    i18n.t('Global.Thursday'),
                    i18n.t('Global.Friday'),
                    i18n.t('Global.Saturday')
                ],

        }));
        $el.i18n();
    },

    events: {
    },
})
