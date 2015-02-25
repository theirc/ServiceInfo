var config = require('./config');
var api = require('./api');
var i18n = require('i18next-client');

var forms = module.exports = {
    collect: function($form) {
        var data = {};

        $form.find('[name]').each(function() {
            var $field = $(this);
            var value = $field.val();
            var filled = value.length > 0;
            var name = $field.attr('name');
            var ml = typeof $field.data('i18n-field') !== "undefined";

            if (filled && name.indexOf('.') > 0) {
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

            if (name.indexOf('.') < 0) {
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
        var self = this;
        var data = model.data();
        $.each(data, function(name, value) {
            self.getField($form, name).val(value);
        })
    },

    populateDropdown: function($form, name, collection) {
        var $field = this.getField($form, name);
        var empty_label_key = $field.attr('data-empty-label-key');
        var empty_label = i18n.t(empty_label_key);

        function resetOptions() {
            var value = $field.val();
            var data = collection.data();
            var empty_option = $('<option/>');
            empty_option.text(empty_label);

            $field.html("");
            $field.append(empty_option)

            var $option;
            for (var i=0; i < data.length; i++) {
                $option = $('<option/>');
                $option.attr('value', data[i].url);
                $option.text(data[i].name);
                $field.append($option);
            }

            $field.val(value);
        }

        resetOptions();
        config.change("forever.language", function() {
            var detached = $form.closest('html').length === 0;
            if (detached) {
                config.unbind("forever.language", arguments.callee);
            } else {
                resetOptions();
            }
        });
    },

    show_errors_on_form: function($form, e) {
        // returns missing...
        var self = this,
            missing = {},
            errors = e.responseJSON;
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
    },

    submit: function($form, action, data, errors) {
        var errors = errors || {};
        var self = this;
        var $submit = $form.find('.form-btn-submit');
        $submit.attr('disabled', 'disabled');

        return new Promise(function(resolve, error) {
            api.request('POST', action, data).then(
                function onsuccess(data) {
                    $submit.removeAttr('disabled');
                    resolve.apply(this, arguments);
                },
                function onerror(e) {
                    $submit.removeAttr('disabled');
                    $.extend(errors, e.responseJSON);
                    var missing = this.show_errors_on_form($form, e);
                    error(missing);
                }
            );
        });
    },
};
