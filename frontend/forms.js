var config = require('./config');
var i18n = require('i18next-client');

module.exports = {
    collect: function($form) {
        var data = {};

        $form.find('[name]').each(function() {
            var $field = $(this);
            var value = $field.val();
            var name = $field.attr('name');
            var ml = typeof $field.data('i18n-field') !== "undefined";

            if (ml) {
                var cur_lang = localStorage['lang'];
                name = name + '_' + cur_lang;
            }

            data[name] = value;
        });

        return data;
    },

    getFieldLabel: function($form, name) {
        var $field = $form.find('[name={}]'.replace('{}', name));
        var id = $field.attr('id');
        return $form.find('label[for='+ id +']');
    },

    submit: function($form, action, data, errors) {
        var errors = errors || {};
        var self = this;
        var $submit = $form.find('.form-btn-submit');
        $submit.attr('disabled', 'disabled');

        return new Promise(function(resolve, error) {
            $.ajax(config.get('api_location')+action, {
                method: 'POST',
                data: data,
                error: function(e) {
                    $submit.removeAttr('disabled');
                    $.extend(errors, e.responseJSON);
                    var missing = {};
                    $.each(errors, function(k) {
                        var $error = self.getFieldLabel($form, k).find('.error');
                        if ($error) {
                            $error.text(this[0]);
                        } else {
                            missing[k] = this[0];
                        }
                    })
                    if (e.status >= 500) {
                        $('.error-submission').text(i18n.t('Global.FormSubmissionError'));
                    }
                    error(missing);
                },
                success: function() {
                    $submit.removeAttr('disabled');
                    resolve.apply(this, arguments);
                },
            });
        });
    },
};
