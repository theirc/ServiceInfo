var hashtrack = require('hashtrack');
var service = require('./models/service');
var servicetype = require('./models/servicetype');
var search_control_template = require('./templates/_search_controls.hbs');
var Backbone = require('backbone');
var config = require('./config');
var messages = require('./messages');
var i18n = require('i18next-client');
var language = require('./language');


var query = "";
var latlon = null;

hashtrack.onhashvarchange('q', function(_, value) {
    query = value;
});
hashtrack.onhashvarchange('t', function(_, value) {
    query = value;
});
hashtrack.onhashvarchange('n', function(_, value) {
    if (value) {
        var parts = value.split(',');
        latlon = {lat: parts[0], lon: parts[1]};
    } else {
        latlon = null;
    }
});

var SearchControls = Backbone.View.extend({
    initialize: function(opts) {
        this.$el = opts.$el;
        this.feedback = opts.feedback;
        var self=this;
        language.ready(function() {
            self.render();
        });
    },
    render: function() {
        var $el = this.$el;
        var q = hashtrack.getVar('q');
        var html = search_control_template({
            query: q,
        });
        $el.html(html);
        module.exports.populateServiceTypeDropdown();
        $el.i18n();

        if (navigator.geolocation) {
            this.findNearMe();
        }

        // Refocus on query input if there is a current value
        var input = $('input.query', $el);
        input.focus();
        if (q) {
            // Change input value to ensure cursor is at the end
            input.val('');
            input.val(q);
        }
    },
    findNearMe: function() {
        // http://diveintohtml5.info/geolocation.html
        var self = this;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                handlePosition,
                handleError,
                {
                    maximumAge: 90000  // okay to cache location up to 90 seconds
                }
            );
        } else {
            messages.add(i18n.t('Global.GeolocationNotSupported'));
        }
        function handlePosition(position) {
            var latlon = position.coords.latitude + "," + position.coords.longitude;
            self.$el.find('[name=sort][value=near]').prop('checked', true);
            hashtrack.setVar('n', latlon);
        }
        function handleError(error) {
            // DiveIntoHTML5 says that 'error' will be an object with a
            // 'code' attribute... but in Chrome I seem to just be getting a number.
            // Deal with it either way.
            if (typeof error === 'number') {
                error = {
                    code: error
                };
            }
            if (error.code === 1) {
                // PERMISSION_DENIED
                // if the user clicks the "Don’t Share" button or otherwise denies you access to their location.
                // Silently carry on
            }
            else if (error.code === 2) {
                // POSITION_UNAVAILABLE
                // if the network is down or the positioning satellites can't be contacted.
                messages.add(i18n.t('Global.GeoPositionUnavailable'));
            }
            else if (error.code === 3) {
                // TIMEOUT
                // if the network is up but it takes too long to calculate the user's position.
                messages.add(i18n.t('Global.GeoPositionUnavailable'));
            }
            else {
                // unexpected
                console.error(error);
            }
        }
    },
    sortByName: function() {
        hashtrack.setVar('n', '');
    },

    events: {
        "click [name=map-toggle-list]": function() {
            hashtrack.setPath(this.feedback ? '/feedback/list' : '/search');
        },
        "click [name=map-toggle-map]": function() {
            hashtrack.setPath(this.feedback ? '/feedback/map' : '/search/map');
        },
        "change [value=name]": function(e) {
            this.sortByName();
        },
        "change [value=near]": function(e) {
            this.findNearMe();
        },
        "input input.query": function(e) {
            var query = $(e.target).val();
            if (this.timeout) {
                clearTimeout(this.timeout);
            }
            this.timeout = setTimeout(function () {
                hashtrack.setVar('q', query);
            }, 500);
        },
        "change .query-service-type": function(e) {
            hashtrack.setVar('t', $(e.target).val());
        },
        "input keyup": function(e) {
            if (e.keyCode === 13) {
                return false;
            }
        }
    }
});

module.exports = {
    services: new service.PublicServices(),
    servicetypes: new servicetype.ServiceTypes(),
    SearchControls: SearchControls,

    populateServiceTypeDropdown: function() {
        var servicetypes = this.servicetypes;
        var $select = $('select.query-service-type');

        servicetypes.fetch().then(function() {
            $select.find('.loading').hide();
            $select.find('.type-header').show();
            $.each(servicetypes.models, function() {
                var d = this.data();
                $select.append('<option value="'+d.number +'">'+d.name+'</option>')
            })
            var t = hashtrack.getVar('t');
            if (t) {
                $select.val(t);
            }
        });
    },

    refetchServices: function() {
        var query = hashtrack.getVar('q');
        var type = hashtrack.getVar('t');
        var params = {
            search: query,
            type_numbers: type,
            limit: 25
        };
        if (latlon) {
            params.closest = latlon.lat + ',' + latlon.lon;
        }
        var services = this.services;

        return new Promise(function(onresolve, onerror) {
            var fetchp = services.fetch({data: params});
            fetchp.then(
                function() {
                    var days = [
                        "Sunday",
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ];
                    var today = days[new Date().getDay()];
                    var todaylc = today.toLowerCase();
                    services.models.forEach(function(service) {
                        var open = service.get(todaylc + '_open');
                        var close = service.get(todaylc + '_close');
                        if (open && close) {
                            service.set("today_open", open);
                            service.set("today_close", close);
                        }
                    });
                    services.loadSubModels().then(function(){
                        onresolve(fetchp);
                    });
                },
                onerror
            );
        });
    },
};
