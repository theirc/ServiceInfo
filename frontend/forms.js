var config = require('./config')
,   api = require('./api')
,   i18n = require('i18next-client')
,   messages = require('./messages')
;

var forms = module.exports = {
    /* collect(form: <form>, model: optional)
     *
     * Collect submission data from a form combined with other language data from the original
     * model, if given.
     */
    collect: function($form, instance) {
        var data = {};

        var collect_field_data = function() {
            var value, filled;
            var $field = $(this);
            if ($field.attr('type') === 'checkbox') {
                filled = value = $field.prop('checked');
            } else {
                value = $field.val();
                filled = value.length > 0;
            }
            var name = $field.attr('name') || $field.parent().attr('name');
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

                // Set all languages if we have an original instance to pull the non-current from
                if (instance) {
                    $.each(['en', 'fr', 'ar'], function() {
                        data[name + '_' + this] = instance.get(name + '_' + this);
                    });
                }

                name = name + '_' + cur_lang;
            }

            if (name.indexOf('.') < 0) {
                data[name] = value;
            }
        };

        $form.find('[name]').not('select, [type=checkbox], [type=radio]').each(collect_field_data);
        $form.find('select[name] option:selected').each(collect_field_data);
        $form.find('input[name][type=checkbox]:checked').each(collect_field_data);
        $form.find('input[name][type=radio]:checked').each(collect_field_data);

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
            var $field = self.getField($form, name);
            if ($field.attr('type') === 'checkbox') {
                // It's a checkbox
                $field.prop('checked', value);
            }
            else {
                $field.val(value);
            }
        })
    },

    populateDropdown: function($form, name, collection) {
        var $field = this.getField($form, name);
        var empty_label_key = $field.attr('data-empty-label-key');
        var empty_label = i18n.t(empty_label_key);

        function resetOptions() {
            var data;
            window.collection = collection;
            if (typeof collection.data === "function") {
                data = collection.data();
            } else {
                data = Array.prototype.slice.apply(collection);
            }
            var value = $field.val();
            var empty_option = $('<option/>');
            empty_option.text(empty_label);

            data.sort(function(a, b){
                var prop = "name";
                return ((a[prop] < b[prop]) ? -1 : ((a[prop] > b[prop]) ? 1 : 0));
            })

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
    },

    clear_form: function($form) {
       $form.find('[name]').each(function() {
            var $field = $(this);
            $field.val('');
        });
    },

    show_errors_on_form: function($form, e) {
        // 'e' should be a jqHXR object with a responseJSON attribute
        // containing a dictionary of the errors
        // returns missing...
        var self = this,
            missing = {},
            errors = e.responseJSON;
        $.each(errors, function(k) {
            if (k === 'non_field_errors') {
                for (var i = 0; i < this.length; i++) {
                    messages.add(this[i]);
                }
            } else {
                var $error = self.getFieldLabel($form, k).parent().find('.error');
                if ($error.length) {
                    $error.text(this[0]);
                } else {
                    missing[k] = this[0];
                }
            }
        })
        if (e.status >= 500) {
            $('.error-submission').text(i18n.t('Global.FormSubmissionError'));
        } else if (e.status === 400) {
            messages.add(i18n.t('Global.FormValidationError'));
        }
        return missing;
    },

    gather_and_submit: function(opts) {
        /* Helper for simple forms.  Pass in {
             el: $el,
             url: url to submit to,
             next_location: location to go to if successful
           }
         */
        opts.el.find('.form-btn-submit').attr('disabled', 'disabled');
        opts.el.find('.error').text('');

        var data = forms.collect(opts.el),
            errors = {};

        forms.submit(opts.el.find('form'), opts.url, data, errors).then(
            function success(data) {
                window.location = opts.next_location;
            },
            function error(errors) {
                // forms.js has already displayed any errors
            }
        );
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
                    $.extend(e.responseJSON, errors);  // merge errors into e.responseJSON
                    messages.clear();
                    var missing = self.show_errors_on_form($form, e);
                    error(missing);
                }
            );
        });
    },
};
