var Backbone = require('backbone'),
    template = require("../templates/service-request-form.hbs"),
    forms = require("../forms"),
    $ = require('jquery'),
    models = require('../models/models'),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({

    render: function() {
        var self = this,
            context = {
                starvalues: [5, 4, 3, 2, 1]
            };

        models.preloaded.then(function(results) {
            var $form;

            self.$el.html(template(context));
            self.$el.i18n();

            $form = self.$el.find('form');
            forms.populateDropdown($form, "area_of_service", results.servicearea);
            forms.populateDropdown($form, "service_type", results.servicetype);
        }, function onerror(error) {
            messages.error(error);
            console.error("Unlogged errors:");
            console.error(error);
        });
    },

    events: {
        "click .form-btn-submit": function(e) {
            e.preventDefault();
            forms.gather_and_submit({
                el: this.$el,
                url: 'api/requestsforservice/',
                next_location: '#/service/request/confirm'
            })
        },
        "click .form-btn-clear": function(e) {
            e.preventDefault();
            forms.clear_form(this.$el);
        }
    }
});
