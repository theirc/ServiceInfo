var config = require('./config');

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

        return new Promise(function(resolve, error) {
            $.ajax(config.get('api_location')+action, {
                method: 'POST',
                data: data,
                error: function(e) {
                    $.extend(errors, e.responseJSON);
                    $.each(errors, function(k) {
                        var $error = self.getFieldLabel($form, k).find('.error');
                        if ($error) {
                            $error.text(this[0]);
                        }
                    })
                    error(errors);
                },
                success: resolve,
            });
        });
    },
};
