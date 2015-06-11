var Backbone = require('backbone'),
    template = require("../templates/search-list.hbs"),
    result_template = require('../templates/_results_template.hbs'),
    service = require('../models/service'),
    servicetype = require('../models/servicetype'),
    i18n = require('i18next-client'),
    search = require('../search'),
    config = require('../config')
;


module.exports = Backbone.View.extend({
    feedback: false,

    initialize: function(params){
        var self = this;
        self.feedback = params.hasOwnProperty('feedback');
    },

    perform_query: function() {
        search.refetchServices().then(this.renderResults);
    },

    render: function() {
        var $el = this.$el;

        this.$el.html(template({
            feedback: this.feedback
        }));
        $('.no-search-results').hide();
        $('.results-truncated').hide();

        // Renders automatically when language is ready
        this.SearchControlView = new search.SearchControls({
            $el: this.$el.find('#search_controls'),
            feedback: this.feedback
        });
        this.SearchControlView.on('search_parameters_changed', this.perform_query, this);

        $el.i18n();
        this.perform_query();
    },

    renderResults: function() {
        var $el = $('.search-result-list');
        var html = result_template({
            services: search.services.data()
        });
        $el.html(html);
        if (search.services.length === 0) {
            $('.no-search-results').show();
        } else {
            $('.no-search-results').hide();
        }
        $('.results-truncated').toggle(search.has_more);
        $el.i18n();
    }
});
