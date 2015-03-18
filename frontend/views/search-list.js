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
        var $el = this.$el;
        search.refetchServices().then(function(){
            var html = result_template({
                services: search.services.data(),
            })
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
        var $el = this.$el;
        var self = this;

        this.$el.html(template({
            query: hashtrack.getVar('q'),
        }));
        this.$el.i18n();

        var $scv = this.$el.find('#search_controls');
        var SearchControlView = new search.SearchControls({
            $el: $scv,
        });
        SearchControlView.render();

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
        var services = search.services.data();

        $.each(services, function() {
            var service = this;
        });

        self.render();
    },

    events: {
        "click button[name=search]": function(e) {
            var self = this;
            hashtrack.setVar('q', self.$el.find('.query').val());
            hashtrack.setVar('t', self.$el.find('.query-service-type').val());
            search.refetchServices().then(function(){
                self.updateResults();
            })
        },
    }
})
