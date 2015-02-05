var Backbone = require('backbone'),
template = require("../templates/service-form.hbs"),
i18n = require('i18next-client'),
forms = require('../forms'),
provider = require('../models/provider'),
servicearea = require('../models/servicearea'),
servicetype = require('../models/servicetype')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        self = this;

        var providers = new provider.Providers();
        var serviceareas = new servicearea.ServiceAreas();
        var servicetypes = new servicetype.ServiceTypes();

        Promise.all([providers.fetch(), serviceareas.fetch(), servicetypes.fetch()]).then(function(){
            self.provider = providers.models[0];
            self.serviceareas = serviceareas;
            self.servicetypes = servicetypes;

            self.render();
        });
    },

    render: function() {
        var $el = this.$el;
        var serviceareas = [];
        if (this.serviceareas) {
            serviceareas = this.serviceareas.data();
        }
        var types = [];
        if (this.servicetypes) {
            types = this.servicetypes.data();
        }
        $el.html(template({
            daysofweek: [
                    'Sunday',
                    'Monday',
                    'Tuesday',
                    'Wednesday',
                    'Thursday',
                    'Friday',
                    'Saturday',
                ],
            areas_of_services: serviceareas,
            types: types,
        }));
        $el.find('[name=provider]').val(this.provider.get('url'));
        $el.i18n();
    },

    events: {
        "click .form-btn-submit": function() {
            var $el = this.$el;
            var data = forms.collect($el);

            $el.find('.error').text('');

            forms.submit($el, 'api/services/', data).then(
                function success(data) {
                    window.location = '#/register/confirm';
                },
                function error(errors) {
                    console.error(errors);
                }
            );

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
