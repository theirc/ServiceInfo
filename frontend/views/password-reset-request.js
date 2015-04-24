/* View to ask to have your password reset.  If successful, user
   is emailed a link to the password-reset-form page that includes
   a limited-time password reset key.
 */
var Backbone = require('backbone'),
    template = require("../templates/password-reset-request.hbs"),
    forms = require('../forms'),
    messages = require('../messages'),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
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
            var email = $el.find('input[name=email]').val();
            var data = {
                email: email,
                base_reset_link: location.protocol + '//' + location.host + location.pathname + '?#/password-reset/'
            };
            forms.submit($form, 'api/password_reset_request/', data).then(
                function on_success() {
                    $submit.removeAttr('disabled');
                    messages.add(i18n.t('Password-Reset.Submitted'));
                },
                function on_error() {
                    $submit.removeAttr('disabled');
                    // forms.js has already displayed any errors
                }
            );
        }
    }
})
