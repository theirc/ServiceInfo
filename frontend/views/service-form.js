var Backbone = require('backbone'),
api = require('../api'),
template = require("../templates/service-form.hbs"),
i18n = require('i18next-client'),
forms = require('../forms'),
models = require('../models/models'),
messages = require('../messages'),
service = require('../models/service'),
servicearea = require('../models/servicearea'),
servicetype = require('../models/servicetype')
;


function remove_empty_fields(data) {
    // Remove items from data that have empty values
    var keys = Object.keys(data);
    for (var i = 0; i < keys.length; i++) {
        if (! data[keys[i]]) {
            delete data[keys[i]];
        }
    }
}

module.exports = Backbone.View.extend({
    initialize: function(opts){
        self = this;
        self.serviceareas = [];
        self.servicetypes = [];

        var waiting = [models.preloaded];
        var current_service;
        if (opts.id) {
            current_service = new service.Service({id: opts.id});
            waiting.push(current_service.fetch());
        }
        messages.clear();

        Promise.all(waiting).then(function onsuccess(results){
            self.serviceareas = results[0].servicearea.data();
            self.servicetypes = results[0].servicetype.data();
            if (opts.id) {
                self.update_of = current_service;
            }

            self.render();
        }, function onerror(e) {
            messages.error(e);
        });
    },

    populateDropdowns: function() {
        var $form = this.$el.find('#service-form');
        forms.populateDropdown($form, "area_of_service", this.serviceareas);
        forms.populateDropdown($form, "type", this.servicetypes);
    },

    render: function() {
        var $el = this.$el;
        var criteria = [];
        if (this.update_of) {
            criteria = self.update_of.data()['selection_criteria'];
        }
        if (criteria.length === 0) {
            criteria.push({text: ""});
        }
        $el.html(template({
            daysofweek: [
                    i18n.t('Global.Sunday'),
                    i18n.t('Global.Monday'),
                    i18n.t('Global.Tuesday'),
                    i18n.t('Global.Wednesday'),
                    i18n.t('Global.Thursday'),
                    i18n.t('Global.Friday'),
                    i18n.t('Global.Saturday')
                ],

            areas_of_services: this.serviceareas,
            types: this.servicetypes,
            criteria: criteria
        }));
        if (this.serviceareas && this.servicetypes) {
            this.populateDropdowns();
        }
        if (this.update_of) {
            forms.initial($el, this.update_of);
            forms.getField($el, 'update_of').val(this.update_of.get('url'));
        }
        $el.i18n();
    },

    events: {
        "click button.remove": function(ev) {
            var $btn = $(ev.target);
            var $row = $btn.closest('.criteria');
            var criteriaCount = $('.criteria').length;
            if (criteriaCount > 1) {
                $row.remove();
            } else {
                $row.find('input').val("");
            }
            return false;
        },
        "click button.add": function(ev) {
            var $btn = $(ev.target);
            var $row = $btn.closest('.criteria');
            var $newRow = $row.clone();
            var $newInput = $newRow.find('input');
            var id = $newInput.attr('id');
            var name = $newInput.attr('name');

            function incr(v) {
                var _ = v.split('.');
                var n = parseInt(_[_.length-1]) + 1;
                _[_.length-1] = n.toString();
                return _.join('.');
            }

            id = incr(id);
            name = incr(name);
            $newInput.attr('id', id);
            $newInput.attr('name', name);
            $newInput.val("");

            //$btn.remove();
            $row.parent().append($newRow);

            return false;
        },
        "click .form-btn-submit": function() {
            messages.clear();
            var $el = this.$el;
            var data = forms.collect($el);
            // Like form fields, omit empty values from the data
            remove_empty_fields(data);
            // change criteria items from strings to dictionaries,
            // omitting blank ones
            var i, name, criteria = [];
            var criteria_length = !!data.selection_criteria ? data.selection_criteria.length : 0;
            for (i = 0; i < criteria_length; i++) {
                name = data.selection_criteria[i];
                if (name) {
                    criteria.push({text_en: name});
                }
            }
            data.selection_criteria = criteria;

            $el.find('.error').text('');

            forms.submit($el, 'api/services/', data).then(
                function success(data) {
                    window.location = '#/service-list';
                },
                function error(errors) {
                    messages.error(errors);
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
