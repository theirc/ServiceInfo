var Backbone = require('backbone'),
    template = require("../templates/service-list.hbs"),
    i18n = require('i18next-client'),
    messages = require('../messages'),
    models = require('../models/service')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.services = new models.Services();
        this.render();
    },

    render: function() {
        messages.clear();
        var $el = this.$el;
        var services = this.services;
        this.services.fetch().then(function(r){
            window.services = services;
            var p = services.loadSubModels();
            p.then(function(){
                var records = services.data();
                for (var i = 0; i < records.length; i++) {
                    records[i].is_draft = records[i].status === 'draft';
                    records[i].is_rejected = records[i].status === 'rejected';
                    records[i].is_current = records[i].status === 'current';
                    if (records[i].update_of) {
                        records[i]._sort = parseInt(records[i].update_of.match(/(\d+)\/$/)[1]) + 0.5;
                    } else {
                        records[i]._sort = parseInt(records[i].url.match(/(\d+)\/$/)[1]);
                    }
                }
                records.sort(function(a, b){ return a._sort > b._sort; });
                $el.html(template({
                    services: records,
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
