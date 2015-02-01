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
                console.log(name + ': ' + value);
            });

            $.ajax('//localhost:4005/api/providers/create_provider/', {
                method: 'POST',
                data: data,
                error: function(e) {
                    $el.find('.error').text('');
                    $.each(e.responseJSON, function(k) {
                        console.log(k + ': ' + this[0]);

                        $el.find('[for='+k+'] .error').text(this[0]);
                    })
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
