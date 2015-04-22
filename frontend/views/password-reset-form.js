/* View for actually changing password. Only works
   if a valid password reset key is included in
   the URL.
 */
var Backbone = require('backbone'),
    config = require('../config'),
    template = require("../templates/password-reset-form.hbs"),
    api = require('../api'),
    forms = require('../forms'),
    messages = require('../messages'),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(opts){
        var self = this;

        self.key = opts.uid + "/" + opts.token;
        self.valid_key = false;
        messages.clear();

        // Is this key valid?
        api.request('POST', 'api/password_reset_check/', {key: this.key}).then(
            function on_success() {
                self.valid_key = true;
                self.render();
            },
            function on_error() {
                self.valid_key = false;
                self.render();
            }
        );
    },

    render: function() {
        this.$el.html(template({
            valid_key: this.valid_key
        }));
        this.$el.i18n();
    },

    events: {
        "click .form-btn-submit": function (e) {
            e.preventDefault();

            var $el = this.$el;
            var $form = $el.find('form');

            var $submit = $form.find('.form-btn-submit');
            $submit.attr('disabled', 'disabled');

            $el.find('.error').text('');
            messages.clear();

            var password1 = $form.find('input[name=password1]').val();
            var password2 = $form.find('input[name=password2]').val();
            var errors;

            function add_error(fieldname, message_key) {
                errors = errors || {};
                errors[fieldname] = [i18n.t(message_key)];
            }

            if (password1 === '') {
                add_error('password1', "Password-Reset-Form.Errors.Password-Blank");
            }
            if (password2 === '') {
                add_error('password2', "Password-Reset-Form.Errors.Password-Repeat");
            }
            if (password1 !== '' && password2 !== '' && password1 !== password2) {
                add_error('password2', "Password-Reset-Form.Errors.Password-Match");
            }
            if (errors) {
                forms.show_errors_on_form($form, {responseJSON: errors});
                $submit.removeAttr('disabled');
                return false;
            }

            var data = {
                key: this.key,
                password: password2
            };
            forms.submit($form, 'api/password_reset/', data).then(
                function on_success(data) {
                    $submit.removeAttr('disabled');
                    messages.add(i18n.t('Password-Reset-Form.Changed'));
                    // "Log them in"
                    config.set('forever.authToken', data.token);
                    // Store the email to make it easier to pick out a user's
                    // own records - this is really just for superusers, everybody
                    // else will only get back their own records anyway.
                    config.set('forever.email', data.email);
                    if (data.language) {
                        config.set('forever.language', data.language);
                    }
                    function gohome() {
                        window.location.hash = '/manage/service-list';
                    }
                    // Go home after some time (milliseconds)
                    window.setTimeout(gohome, 3000);
                },
                function on_error() {
                    $submit.removeAttr('disabled');
                    // forms.js has already displayed any errors
                }
            );
        }

    }
});
