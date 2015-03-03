var Backbone = require('backbone'),
api = require('../api'),
template = require("../templates/service-detail.hbs"),
i18n = require('i18next-client'),
models = require('../models/models'),
messages = require('../messages')
;

module.exports = Backbone.View.extend({
    initialize: function(opts){
        self = this;
        messages.clear();
        var service = new models.service.Service({id: opts.id});

        service.fetch().then(function onsuccess(){
            console.log(opts, service.data());
            service.loadSubModels().then(function(){
                self.render();
            })
        }, function onerror(e) {
            messages.error(e);
        });

        this.service = service;
    },

    render: function() {
        var $el = this.$el;
        $el.html(template({
            service: this.service.data(),
            daysofweek: [
                    i18n.t('Global.Sunday'),
                    i18n.t('Global.Monday'),
                    i18n.t('Global.Tuesday'),
                    i18n.t('Global.Wednesday'),
                    i18n.t('Global.Thursday'),
                    i18n.t('Global.Friday'),
                    i18n.t('Global.Saturday')
                ],

        }));
        $el.i18n();
    },

    events: {

    },
})
