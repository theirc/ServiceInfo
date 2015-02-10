var Backbone = require('backbone'),
template = require("../templates/provider-form.hbs"),
i18n = require('i18next-client'),
config = require('../config'),
providertype = require('../models/providertype'),
forms = require('../forms')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        self = this;

        var providertypes = new providertype.ProviderTypes();

        Promise.all([providertypes.fetch()]).then(function(){
            self.providertypes = providertypes;
            self.render();
        });
    },

    render: function() {
        var $el = this.$el;
        var providertypes = [];
        if (self.providertypes) {
            providertypes = self.providertypes.data();
        }

        $el.html(template({
            "providertypes": providertypes,
        }));
        $el.i18n();
    },

    events: {
        "click .form-btn-submit": function() {
            var $el = this.$el;
            var data = forms.collect($el);

            $el.find('.error').text('');
            var errors = {};

            // Password Handling

            if (data['password1'].length === 0) {
                errors['password1'] = [i18n.t('Provider-Registration-Form.Errors.Password-Blank')];
            }
            if (data['password2'].length === 0) {
                errors['password2'] = [i18n.t('Provider-Registration-Form.Errors.Password-Repeat')];
            } else if (data['password1'] != data['password2']) {
                errors['password2'] = [i18n.t('Provider-Registration-Form.Errors.Password-Match')];
            }
            if (!errors['password1'] && !errors['password2']) {
                data['password'] = data['password1'];
                delete data.password1;
                delete data.password2;
            }

            // Base Activation Link
            data["base_activation_link"] = location.protocol+'//'+location.host+location.pathname+'?#/register/verify/';

            forms.submit($el, 'api/providers/create_provider/', data, errors).then(
                function success(data) {
                    window.location = '#/register/confirm';
                },
                function error(errors) {
                    console.error(errors);
                }
            );

            return false;
        },
        "click .form-btn-clear": function() {
            this.$el.find('[name]').each(function() {
                var $field = $(this);
                $field.val('');
            });
            return false;
        },
    },
})
