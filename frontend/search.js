var hashtrack = require('hashtrack');
var service = require('./models/service');
var servicetype = require('./models/servicetype');
var search_control_template = require('./templates/_search_controls.hbs');
var Backbone = require('backbone');
var config = require('./config');
var messages = require('./messages');
var i18n = require('i18next-client');
var language = require('./language');


// If not null, latlon is the person's current position as
// {lat: N; lon: M}
var latlon = null;

var deny_permission = false;  // pretend user denied location permission

var MAX_RESULTS = 25;

var SearchControls = Backbone.View.extend({
    initialize: function(opts) {
        this.$el = opts.$el;
        this.feedback = opts.feedback;
        var self=this;
        language.ready(function () {
            self.render();
        });
    },
    render: function() {
        var $el = this.$el;
        var q = config.get('q'); // string for text search
        var s = config.get('s') || 'n'; // sort by 'n'=name or 'd'=distance
        var html = search_control_template({
            query: q,
            sort_by_name: s === 'n',
            sort_by_distance: s === 'd'
        });
        $el.html(html);
        module.exports.populateServiceTypeDropdown();
        $el.i18n();

        // Refocus on query input if there is a current value
        var input = $('input.query', $el);
        input.focus();
        if (q) {
            // Change input value to ensure cursor is at the end
            input.val('');
            input.val(q);
        }
    },
    events: {
        "click [name=map-toggle-list]": function() {
            hashtrack.setPath(this.feedback ? '/feedback/list' : '/search');
        },
        "click [name=map-toggle-map]": function() {
            hashtrack.setPath(this.feedback ? '/feedback/map' : '/search/map');
        },
        "change [value=name]": function(e) {
            messages.clear();
            config.set('s', 'n');
            this.trigger('search_parameters_changed');
        },
        "change [value=near]": function(e) {
            messages.clear();
            config.set('s', 'd');
            this.trigger('search_parameters_changed');
        },
        "input input.query": function(e) {
            var query = $(e.target).val();
            if (this.timeout) {
                clearTimeout(this.timeout);
            }
            var self = this;
            this.timeout = setTimeout(function () {
                config.set('q', query);
                self.trigger('search_parameters_changed');
            }, 500);
        },
        "change .query-service-type": function(e) {
            config.set('t', $(e.target).val());
            this.trigger('search_parameters_changed');
        },
        "input keyup": function(e) {
            if (e.keyCode === 13) {
                return false;
            }
        }
    }
});

var findUserPosition = function() {
    // Returns a promise that resolves when we figure out the user's location, or
    // fail to.
    return new Promise(function(resolve) {
        if (deny_permission) { // for testing, pretend user denied permission.
            handleError(1);
            return;
        }
        // http://diveintohtml5.info/geolocation.html
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
            latlon = null;
            if (config.get('s') !== 'n') {
                config.set('s', 'n');
            }
            resolve();
        }

        function handlePosition(position) {
            latlon = {lat: position.coords.latitude, lon: position.coords.longitude};
            resolve();
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
                messages.add(i18n.t('Global.GeoLocationDenied'));
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
            /* In any case, we can't sort by distance */
            latlon = null;
            if (config.get('s') !== 'n') {
                config.set('s', 'n');
            }
            resolve();
        }
    });
};

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
            var t = config.get('t');
            if (t) {
                $select.val(t);
            }
        });
    },

    refetchServices: function() {
        /* Returns a Promise that when resolved returns the collection of services.
           Or you can just access the collection at search.services.
         */
        var self = this;

        // Start with an already resolved promise, then chain onto it:
        var sequence = Promise.resolve();

        if (config.get('s') === 'd' && latlon === null) {
            // requested to sort by distance but we don't know where the user is.
            // Need to query first, so add that onto our sequence of tasks:
            sequence = sequence.then(findUserPosition);
            // now sequence won't resolve until we've gotten the location
        }

        // Now we can add onto our sequence the actual fetch of the services.
        // It won't start until we've gotten the location, if we needed to.
        // It'll resolve when the services have been fetched.
        sequence = sequence.then(function() {
            var params = {
                search: config.get('q'),
                type_numbers: config.get('t'),
                limit: MAX_RESULTS
            };
            if (latlon && config.get('s') === 'd') {
                params.closest = latlon.lat + ',' + latlon.lon;
            }
            // Return the promise so the new sequence won't resolve until the fetch is done.
            return self.services.fetch({data: params});
        });

        // Once fetch is done, process the results some more:
        sequence = sequence.then(function(response) {
            var days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
            ];
            self.has_more = (response.next !== null);
            var today = days[new Date().getDay()];
            var todaylc = today.toLowerCase();
            var services = self.services;
            services.models.forEach(function(service) {
                var open = service.get(todaylc + '_open');
                var close = service.get(todaylc + '_close');
                if (open && close) {
                    service.set("today_open", open);
                    service.set("today_close", close);
                }
            });
            // Return a new promise that won't resolve until we've got the submodels too.
            return services.loadSubModels();
        });

        // Finally return the end promise:
        return sequence;
    }
};
