var Backbone = require('backbone'),
api = require('../api'),
config = require('../config'),
template = require("../templates/service-cancel.hbs"),
i18n = require('i18next-client'),
forms = require('../forms'),
service = require('../models/service')
;

module.exports = Backbone.View.extend({
    initialize: function(opts){
        var self = this;
        var current_service = new service.Service({id: opts.id});

        Promise.all([current_service.fetch()]).then(function(){
            self.service = current_service;
            self.update_of = undefined;
            if (current_service.get('update_of')) {
                var update_of = new service.Service({url: current_service.get('update_of')});
                Promise.all([update_of.fetch()]).then(function() {
                    self.update_of = update_of.data();
                    self.render();
                })
            } else {
                self.render();
            }
        });
    },

    render: function() {
        if (this.service) {
            var $el = this.$el;
            $el.html(template({
                is_draft: this.service.get('status') === 'draft',
                update_of: this.update_of,
                service: this.service.data()
            }));
            forms.initial($el, this.service);
            $el.i18n();
        }
    },

    events: {
        "click .form-btn-submit": function() {
            var data = forms.collect(this.$el);
            var path = 'api/services/' + data.id + '/cancel/';
            api.request('POST', path).then(
                function success(resp) {
                    window.location = "#/service-list";
                },
                function error(e) {
                    console.error(e);
                }
            );

            return false;
        }
    },
})
