var Backbone = require('backbone'),
    template = require("../templates/account-activation-failed.hbs"),
    i18n = require('i18next-client'),
    forms = require('../forms')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template());
        $el.i18n();
    },

    events: {
        "click #id_submit": function() {
            ev.preventDefault();
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
