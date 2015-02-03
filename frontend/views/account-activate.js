var Backbone = require('backbone'),
    template = require("../templates/account-activate.hbs"),
    i18n = require('i18next-client'),
    config = require('../config')
;

var Activation = Backbone.Model.extend({
    initialize: function() {
        this.set('status', i18n.t("Account-Activation.Status.Pending"));

        $.ajax(config.get('api_location') + 'api/activate/', {
            type: 'POST',
            // contentType: 'JSON',
            data: {
                'activation_key': this.get('key'),
            },
            success: function(resp) {
                config.set('forever.authToken', resp.token);
            },
            error: function(e) {
                console.error(e);
            },
        })
    },
})

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function(key) {
        var $el = this.$el;
        var activation = new Activation({key: key});
        this.$el.html(template());
    },
})
