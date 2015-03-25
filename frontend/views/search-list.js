var Backbone = require('backbone'),
    template = require("../templates/search-list.hbs"),
    result_template = require('../templates/_results_template.hbs'),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client'),
    search = require('../search')
;


var SearchResultList = Backbone.View.extend({
    render: function() {
        var $el = this.$el;
        var self = this;
        search.refetchServices().then(renderResults)

        config.change("forever.language", function() {
            var detached = $el.closest('html').length === 0;
            if (detached) {
                config.unbind("forever.language", arguments.callee);
            } else {
                renderResults();
            }
        });

        function renderResults() {
            var $el = $('.search-result-list');
            var html = result_template({
                services: search.services.data(),
            })
            $el.html(html);
            $el.i18n();
        }
    },
});


module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this;
        this.query = "";
        // this.render();
    },

    render: function() {
        var $el = this.$el;
        var self = this;

        this.$el.html(template({
            query: hashtrack.getVar('q'),
        }));

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

        $el.i18n();
    },

    updateResults: function() {
        var self = this;
        var services = search.services.data();

        $.each(services, function() {
            var service = this;
        });

        self.resultView.render();
    },

    events: {
        // "click button[name=search]": function(e) {
        //     var self = this;
        //     hashtrack.setVar('q', self.$el.find('.query').val());
        //     hashtrack.setVar('t', self.$el.find('.query-service-type').val());
        //     search.refetchServices().then(function(){
        //         self.updateResults();
        //     })
        // },
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
        "input keyup": function(e) {
            if (e.keyCode === 13) {
                return false;
            }
        },
    }
})
