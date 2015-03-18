var Backbone = require('backbone'),
    template = require("../templates/login.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    messages = require('../messages'),
    api = require('../api'),
    $ = require('jquery')
;

function toggleLoginMenuItem() {
    $('.menu-item-login, .menu-item-logout, .menu-item-staff').hide();
    if (config.get('forever.authToken')) {
        $('.menu-item-login').hide();
        $('.menu-item-logout').show();
        $('.menu-item-staff').toggle(config.get('forever.isStaff'));
    } else {
        $('.menu-item-login').show();
        $('.menu-item-logout').hide();
        $('.menu-item-staff').hide();
    }
};
config.change('forever.authToken', toggleLoginMenuItem);
$(function() {
    toggleLoginMenuItem();
})


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
            messages.clear();
            var $el = this.$el;
            ev.preventDefault();
            var email = $el.find('[name=email]').val();
            var data = {
                email: email,
                password: $el.find('[name=password]').val(),
            };

            $.ajax(api.getAPIPrefix() + 'api/login/', {
                method: 'POST',
                type: 'JSON',
                data: data,
                error: function(e) {
                    console.error("login fail:", e.responseJSON);
                    $('.error').text('');
                    for (var k in e.responseJSON) {
                        if (k == 'non_field_errors') {
                            $el.find('.non-field-errors').text(e.responseJSON[k]);
                        } else if (e.responseJSON.hasOwnProperty(k)) {
                            $el.find('.error-' + k).text(e.responseJSON[k]);
                        }
                    }
                    if (e.status >= 500) {
                       $el.find('.error-submission').text(i18n.t('Global.FormSubmissionError'));
                    }
                },
                success: function(data) {
                    // save isStaff before authToken because when authToken is saved,
                    // we'll update the menus which will look at isStaff
                    config.set('forever.isStaff', data.is_staff);
                    config.set('forever.authToken', data.token);
                    // Store the email to make it easier to pick out a user's
                    // own records - this is really just for superusers, everybody
                    // else will only get back their own records anyway.
                    config.set('forever.email', email);
                    if (data.language) {
                        config.set('forever.language', data.language);
                    }
                    window.location.hash = 'service-list';
                },
            })
        }
    }
})
