var Backbone = require('backbone'),
    template = require("../templates/login.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    $ = require('jquery')
;

$(function() {
    toggleLoginMenuItem();
})

function toggleLoginMenuItem() {
    if (config.get('forever.authToken')) {
        $('.menu-item-login').hide();
    }
};

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
            var $el = this.$el;
            ev.preventDefault();
            var data = {
                email: $el.find('[name=email]').val(),
                password: $el.find('[name=password]').val(),
            };

            $.ajax(config.get('api_location') + 'api/login/', {
                method: 'POST',
                type: 'JSON',
                data: data,
                error: function(e) {
                    console.error("login fail:", e.responseJSON);
                    for (var k in e.responseJSON) {
                        if (e.responseJSON.hasOwnProperty(k)) {
                            $el.find('.error-' + k).text(e.responseJSON[k]);
                        }
                    }
                },
                success: function(data) {
                    config.set('forever.authToken', data.token);
                    toggleLoginMenuItem();
                    router = new Backbone.Router();
                    router.navigate('', {trigger: true});
                },
            })
        }
    }
})
