var Backbone = require('backbone'),
    resend_verification_template = require("../templates/account-resend-verification.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    forms = require('../forms')
    api = require('../api')
;

module.exports = Backbone.View.extend({
    template: resend_verification_template,

    initialize: function(opts){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        $el.html(this.template());
        $el.i18n();
    },

    events: {
        "click #id_submit": function() {
            var self = this;
            var $form = $('#resend-form');
            var data = forms.collect($form);
            var action = 'api/resend_activation_link/';

            data["base_activation_link"] = location.protocol + '//' + location.host + location.pathname + '?#/register/verify/';

            forms.submit($form, action, data).then(
                function onsuccess() {
                    window.location.hash = '';
                    window.location.reload();
                },
                function onerror(e) {
                    console.error(e);
                }
            )

            return false;
        },
    },
})
