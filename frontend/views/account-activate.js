var Backbone = require('backbone'),
    template = require("../templates/account-activate.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    forms = require('../forms')
;

var Activation = Backbone.Model.extend({
    initialize: function() {
        var self = this;
        self.set('status', "Pending");

        $.ajax(config.get('api_location') + 'api/activate/', {
            type: 'POST',
            // contentType: 'JSON',
            data: {
                'activation_key': self.get('key'),
            },
            success: function(resp) {
                config.set('forever.authToken', resp.token);
                config.set('forever.email', resp.email);
                self.set('status', 'Success');
            },
            error: function(e) {
                self.set('status', 'Failed');
            },
        })
    },
})

module.exports = Backbone.View.extend({
    initialize: function(opts){
        var $this = this;
        this.activation = new Activation({key: opts.key});
        this.activation.on('change', function() {
            $this.render();
        });
    },

    render: function() {
        var $el = this.$el;
        var status = this.activation.get('status');
        this.$el.html(template({
            status: status,
            failed: status == 'Failed',
        }));
        $el.i18n();
    },

    events: {
        "click #resend-form": function() {
            var self = this;
            var $form = $('#resend-form');
            var data = forms.collect($form);
            var action = 'api/resend_activation_link/';

            data["base_activation_link"] = location.protocol + '//' + location.host + location.pathname + '?#/register/verify/';

            forms.submit($form, action, data).then(
                function onsuccess() {
                    self.activation.set('status', 'Resent');
                },
                function onerror(e) {
                    console.error(e);
                }
            )

            return false;
        },
    },
})
