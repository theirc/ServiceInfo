var Backbone = require('backbone'),
    config = require('../config'),
    template = require("../templates/service-list.hbs"),
    i18n = require('i18next-client'),
    messages = require('../messages'),
    models = require('../models/service')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.services = new models.Services();
        this.render();

        /* Render again if language changes */
        var $el = this.$el;
        var self = this;
        config.change("forever.language", function() {
            var detached = $('table#service-status').length === 0;
            if (detached) {
                config.unbind("forever.language", arguments.callee);
            } else {
                self.render();
            }
        });
    },

    render: function() {
        messages.clear();
        var $el = this.$el;
        var services = this.services;
        this.services.fetch().then(function(r){
            var no_services = services.length === 0;
            var p = services.loadSubModels();
            p.then(function(){
                var records = services.data();
                for (var i = 0; i < records.length; i++) {
                    records[i].is_draft = records[i].status === 'draft';
                    records[i].is_rejected = records[i].status === 'rejected';
                    records[i].is_current = records[i].status === 'current';
                    records[i].is_update = ! records[i].is_current;
                    if (records[i].update_of) {
                        records[i]._sort = parseInt(records[i].update_of.match(/(\d+)\/$/)[1]) + 0.5;
                    } else {
                        records[i]._sort = parseInt(records[i].url.match(/(\d+)\/$/)[1]);
                    }
                    records[i].servicearea = records[i].servicearea;
                    records[i].servicetype = records[i].servicetype;
                }
                records.sort(function(a, b){ return a._sort > b._sort; });
                $el.html(template({
                    services: records,
                    no_services: no_services,
                }));
                $el.i18n();
            }, function onerror(e) {
                messages.error(e);
            });
        }, function onerror(e) {
            messages.error(e);
        });
    },

    events: {
    },
})
