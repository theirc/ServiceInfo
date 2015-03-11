var Backbone = require('backbone'),
    template = require("../templates/search-list.hbs"),
    result_template = require('../templates/_results_template.hbs')
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client'),
    search = require('../search')
;


var SearchResultList = Backbone.View.extend({
    render: function() {
        console.log("R2");
        var $el = this.$el;
        search.services.fetch().then(function(){
            console.log("R3");
            console.log("services:", search.services.models);
            var html = result_template({
                services: search.services.data(),
            })
            console.log(html);
            console.log($el);
            $('.search-result-list').html(html)
        })
    },
});


module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this;
        this.query = "";
        this.render();
    },

    render: function() {
        console.log("R1");
        var $el = this.$el;
        var self = this;

        this.$el.html(template({
            query: hashtrack.getVar('q'),
        }));

        var $results = $('.search-result-list');
        this.resultView = new SearchResultList({
            $el: $results,
            services: this.services,
        });
        this.resultView.render();

        search.populateServiceTypeDropdown();
    },

    updateResults: function() {
        var self = this;
        var bounds = new google.maps.LatLngBounds();
        var services = search.services.data();

        $.each(services, function() {
            var service = this;

        });
    },

    events: {
        "search": function(_, query) {
            var self = this;
            search.refetchServices().then(function(){
                self.updateResults();
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
