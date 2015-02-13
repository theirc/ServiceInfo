var config = require('./config');
var i18n = require('i18next-client');

var forms = module.exports = {
    collect: function($form) {
        var data = {};

        $form.find('[name]').each(function() {
            var $field = $(this);
            var value = $field.val();
            var name = $field.attr('name');
            var ml = typeof $field.data('i18n-field') !== "undefined";

            if (!!value && name.indexOf('.') > 0) {
                var parts = name.split('.');
                var target = data;
                var tval, fromarray;
                while (parts.length) {
                    if (parts.length > 1) {
                        tval = target[parts[0]];
                        if (typeof tval === 'undefined') {
                            tval = [];

                        } else if ($.isArray(tval) && !$.isNumeric(parts[1])) {
                            fromarray = tval;
                            tval = {};
                            for (var i=0; i<fromarray.length; i++) {
                                tval[i.toString()] = fromarray[i];
                            }
                        }

                        tval[parts[1]] = value;
                        target[parts[0]] = tval;
                    }
                    parts.splice(0, 1);
                    target = tval;
                }
            }

            if (ml) {
                var cur_lang = config.get('forever.language');
                name = name + '_' + cur_lang;
            }

            if (!!value && name.indexOf('.') < 0) {
                data[name] = value;
            }
        });

        return data;
    },

    getField: function($form, name) {
        var $field = $form.find('[name='+name+']');
        return $field;
    },
    getFieldLabel: function($form, name) {
        var $field = $form.find('[name='+name+']');
        var id = $field.attr('id');
        return $form.find('label[for='+ id +']');
    },

    initial: function($form, model) {
        var data = model.data();
        $.each(data, function(name, value) {
            forms.getField($form, name).val(value);
        })
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
