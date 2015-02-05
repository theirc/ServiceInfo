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
};
