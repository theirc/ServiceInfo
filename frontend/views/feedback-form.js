var Backbone = require('backbone'),
    template = require("../templates/feedback-form.hbs"),
    forms = require("../forms"),
    $ = require('jquery'),
    nationality = require('../models/nationality'),
    service = require('../models/service'),
    servicearea = require('../models/servicearea'),
    models = require('../models/models')
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    skip_initial_render: true,

    initialize: function(opts){
        var $el = this.$el,
            self = this;
        self.nationalities = [];
        self.serviceareas = [];

        var public_services = new models.service.PublicServices();

        var waiting = [
            models.preloaded,
            public_services.fetch({data:{id: opts.id}})
        ];

        Promise.all(waiting).then(function(results){
            self.serviceareas = results[0].servicearea.data();
            self.nationalities = results[0].nationality.data();

            self.service = public_services.models[0];
            self.service.loadSubModels().then(function(){
                self.service = self.service.data();
                i18n.init(function() {
                    self.render();
                })
            });
        }, function onerror(error) {
            messages.error(error);
            console.error("Unlogged errors:");
            console.error(error);
        });
    },

    populateDropdowns: function() {
        var $form = this.$el.find('form');
        forms.populateDropdown($form, "area_of_residence", this.serviceareas);
        forms.populateDropdown($form, "nationality", this.nationalities);
    },

    render: function() {
        var context = {
            service: this.service,
            starvalues: [5, 4, 3, 2, 1]
        };

        this.$el.html(template(context));
        this.$el.i18n();
        this.populateDropdowns();

        // hide the conditional ones to start
        $('.ifdelivered, .ifnotdelivered, #row_other_difficulties').hide();

        // Don't allow submit until they've said if the service was delivered
        $('button.form-btn-submit').hide()
    },

    events: {
        "change [name=delivered]": function() {
            var delivered = $('[name=delivered]:checked').val() === "1";
            $('.hideuntildelivered').show();
            $('.ifdelivered').toggle(delivered);
            $('.ifnotdelivered').toggle(!delivered);
            $('button.form-btn-submit').show()
        },
        "change [name=difficulty_contacting]": function() {
            var difficulty = $("#id_difficulty_contacting option:selected").val();
            $('#row_other_difficulties').toggle(difficulty === 'other');
        },
        "click .form-btn-submit": function(e) {
            e.preventDefault();
            var $el = this.$el;
            var data = forms.collect($el);
            var $submit = $el.find('.form-btn-submit');
            $submit.attr('disabled', 'disabled');
            $el.find('.error').text('');
            var errors = {};
            forms.submit($el, 'api/feedback/', data, errors).then(
                function success(data) {
                    $submit.removeAttr('disabled');
                    window.location = '#/feedback/confirm';
                },
                function error(errors) {
                    $submit.removeAttr('disabled');
                    // forms.js has already displayed any errors
                }
            );
        },
        "click .form-btn-clear": function(e) {
            e.preventDefault();
            this.$el.find('[name]').each(function() {
                var $field = $(this);
                $field.val('');
            });
            return false;
        }
    }
});
