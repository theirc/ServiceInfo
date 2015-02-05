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

    submit: function($form, action, data, errors) {
        var errors = errors || {};

        return new Promise(function(resolve, error) {
            $.ajax(config.get('api_location')+action, {
                method: 'POST',
                data: data,
                error: function(e) {
                    $.extend(errors, e.responseJSON);
                    $.each(errors, function(k) {
                        var $error = $form.find('[for='+k+'] .error');
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
