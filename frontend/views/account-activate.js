var Backbone = require('backbone'),
    account_activate_template = require("../templates/account-activate.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    messages = require('../messages'),
    api = require('../api'),
    resend_verification = require('./account-resend-verification')

;

var Activation = Backbone.Model.extend({
    initialize: function() {
        var self = this;
        self.set('status', "Pending");

        messages.clear();
        $.ajax(api.getAPIPrefix() + 'api/activate/', {
            type: 'POST',
            // contentType: 'JSON',
            data: {
                'activation_key': self.get('key'),
            },
            success: function(resp) {
                config.set('forever.authToken', resp.token);
                config.set('forever.email', resp.email);
                config.remove('temp.email');
                window.location = '#/'
            },
            error: function(e) {
                messages.add(e.responseJSON.activation_key);
                // changing the status will trigger an event handler to render the page again:
                self.set('status', 'Failed');
            },
        })
    },
})

module.exports = resend_verification.extend({
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
        $el.html(account_activate_template({
            status: status,
            failed: status === 'Failed'
        }));
        $el.i18n();
    },
})
