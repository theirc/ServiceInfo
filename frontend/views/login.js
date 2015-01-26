var Backbone = require('backbone'),
    template = require("../templates/login.hbs"),
    i18n = require('i18next-client'),
    config = require('../config')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
    },

    events: {
        "click button": function(ev) {
            ev.preventDefault();
            var data = {
                email: this.$el.find('[name=username]').val(),
                password: this.$el.find('[name=password]').val(),
            };

            console.log('api', config.get('api_location'));

            $.ajax(config.get('api_location') + 'api/login/', {
                method: 'POST',
                type: 'JSON',
                data: data,
                error: function(e) {
                    console.error("login fail:", e);
                },
                success: function(data) {
                    config.set('forever.authToken', data.token);
                },
            })
        }
    }
})
