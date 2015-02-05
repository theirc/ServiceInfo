var Backbone = require('backbone'),
template = require("../templates/provider-form.hbs"),
i18n = require('i18next-client');
var config = require('../config');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        $el.html(template({

        }));

        config.load('providertypes', function(e, data) {
            $typeSel = $el.find('select[name=type]');
            $.each(data, function() {
                $option = $('<option></option>');
                $option.attr({
                    value: this.url,
                });
                $option.text(this['name_' + config.get('lang')]);
                $typeSel.append($option)
            })
        })
    },

    events: {
        "click .form-btn-submit": function() {
            var data = {};
            var $el = this.$el;


            $el.find('[name]').each(function() {
                var $field = $(this);
                var value = $field.val();
                var name = $field.attr('name');
                var ml = typeof $field.data('i18n-field') !== "undefined";

                if (ml) {
                    var cur_lang = localStorage['lang'];
                    name = name + '_' + cur_lang;
                }

                data[name] = value;
                // console.log(name + ': ' + value);
            });

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

            $.ajax(config.get('api_location')+'api/providers/create_provider/', {
                method: 'POST',
                data: data,
                error: function(e) {
                    $.extend(errors, e.responseJSON);
                    $.each(errors, function(k) {
                        console.log(k + ' (error): ' + this[0]);

                        var $error = $el.find('[for='+k+'] .error');
                        if ($error) {
                            $error.text(this[0]);
                        }
                    })
                },
                success: function(data) {
                    window.location = '#/register/confirm';
                },
            });

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
