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
            console.log($typeSel);
        })

        console.log($el);
    },

    events: {
        "click .form-btn-submit": function() {
            var data = {};
            var $el = this.$el;


            $el.find('[name]').each(function() {
                var $field = $(this);
                var value = $field.val();
                var name = $field.attr('name');
                var ml = typeof $field.data('i18n-field')==="undefined" ? false : true;

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
                errors['password1'] = ["Password must not be blank"];
            }
            if (data['password2'].length === 0) {
                errors['password2'] = ["Password must be repeated"];
            } else if (data['password1'] != data['password2']) {
                errors['password2'] = ["Passwords must match"];
            }
            if (!errors['password1'] && !errors['password2']) {
                data['password'] = data['password1'];
                delete data.password1;
                delete data.password2;
            }

            // Base Activation Link
            data["base_activation_link"] = location.protocol+'//'+location.host+location.pathname+'?#/register/verify/';

            $.ajax('//localhost:4005/api/providers/create_provider/', {
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
