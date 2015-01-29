var Backbone = require('backbone'),
template = require("../templates/provider-form.hbs"),
i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        $el.html(template({

        }));

        console.log($el);
    },

    events: {
        "click .form-btn-submit": function() {
            var data = {};
            this.$el.find('[name]').each(function() {
                var $field = $(this);
                var value = $field.val();
                var name = $field.attr('name');
                var ml = typeof $field.data('i18n-field')==="undefined" ? false : true;

                if (ml) {
                    var cur_lang = localStorage['lang'];
                    name = name + '_' + cur_lang;
                }

                data[name] = value;
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
