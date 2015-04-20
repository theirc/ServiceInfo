var Backbone = require('backbone'),
    template = require("../templates/search-list.hbs"),
    result_template = require('../templates/_results_template.hbs'),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    hashtrack = require('hashtrack'),
    i18n = require('i18next-client'),
    search = require('../search'),
    config = require('../config')
;


function renderResults() {
    var $el = $('.search-result-list');
    var html = result_template({
        services: search.services.data(),
    })
    $el.html(html);
    $el.i18n();
}

var SearchResultList = Backbone.View.extend({
    render: function() {
        var $el = this.$el;
        var self = this;
        search.refetchServices().then(renderResults);
    },
});


module.exports = Backbone.View.extend({
    feedback: false,

    initialize: function(params){
        var self = this;
        this.query = "";
        self.feedback = params.hasOwnProperty('feedback');
    },

    render: function() {
        var $el = this.$el;
        var self = this;

        this.$el.html(template({
            query: hashtrack.getVar('q'),
            feedback: this.feedback
        }));
        $('.no-search-results').hide();

        var $scv = this.$el.find('#search_controls');
        this.SearchControlView = new search.SearchControls({
            $el: $scv,
            feedback: this.feedback
        });
        this.SearchControlView.render();

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

        if (services.length === 0) {
            $('.no-search-results').show();
            $('.search-result-list').hide();
            return;
        }
        $('.search-result-list').show();
        $('.no-search-results').hide();

        $.each(services, function() {
            var service = this;
        });

        self.resultView.render();
    },

    events: {
        "search": function(_, query) {
            $('.spinner').show();
            var self = this;
            search.refetchServices().then(function(){
                self.updateResults();
                $('.spinner').hide();
            })
        }
    },

    undelegateEvents: function () {
        Backbone.View.prototype.undelegateEvents.apply(this, arguments);
        if (this.SearchControlView) {
            this.SearchControlView.undelegateEvents();
        }
        if (this.resultView) {
            this.resultView.undelegateEvents();
        }
    }
})
