var Backbone = require('backbone'),
template = require("../templates/provider-form.hbs"),
i18n = require('i18next-client'),
config = require('../config'),
messages = require('../messages'),
provider = require('../models/provider'),
providertype = require('../models/providertype'),
user = require('../models/user'),
forms = require('../forms')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        var self = this,
            providers,
            users;

        var providertypes = new providertype.ProviderTypes();
        var waiting = [providertypes.fetch()];

        self.provider = undefined;
        self.user = undefined;

        if (config.get('forever.authToken')) {
            // logged in - probably already have a provider, definitely have a user.
            providers = new provider.Providers();
            waiting.push(providers.fetch());
            users = new user.Users();
            waiting.push(users.fetch());
        }

        Promise.all(waiting).then(function(){
            self.providertypes = providertypes;
            if (providers) {
                // Find this user's user and provider record, in case they're superuser
                self.user = users.where({'email': config.get('forever.email')})[0];
                self.provider = providers.where({'user': self.user.get('url')})[0];
            }
            self.render();
        }, function onerror(error) {
            messages.error(error);
        });
    },

    render: function() {
        var $el = this.$el;
        var providertypes = [];
        var self = this;
        if (self.providertypes) {
            providertypes = self.providertypes.data();
        }
        var is_new = self.provider === undefined;
        var context = {
            "providertypes": providertypes,
            "is_new": is_new
        };
        if (self.provider) {
            context.provider = self.provider.data();
            $.extend(context.provider, self.user.data());
        }
        $el.html(template(context));
        $el.i18n();
        if (self.provider) {
            forms.initial($el, self.provider);
            forms.initial($el, self.user);
        }
    },

    events: {
        "click .form-btn-submit": function() {
            var $el = this.$el;
            var data = forms.collect($el);
            var is_new = this.provider === undefined;

            $el.find('.error').text('');
            var errors = {};

            // Password Handling
            // For now anyway, not handling password changes on this page
            if (is_new) {
                // Must provide password
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
                    if ('password1' in data) {
                        delete data.password1;
                    }
                    if ('password2' in data) {
                        delete data.password2;
                    }
                }
            }

            // Base Activation Link
            if (is_new) {
                data["base_activation_link"] = location.protocol + '//' + location.host + location.pathname + '?#/register/verify/';

                forms.submit($el, 'api/providers/create_provider/', data, errors).then(
                    function success(data) {
                        window.location = '#/register/confirm';
                    },
                    function error(errors) {
                        messages.error(error);
                    }
                );

            } else {
                var user_save = this.user.save({email: data.email});
                delete data.email;
                var provider_save = this.provider.save(data);
                Promise.all([user_save, provider_save]).then(
                    function success(data) {
                        window.location = '#/register/changed';
                    },
                    function error(errors) {
                        messages.error(error);
                    }
                );
            }

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
