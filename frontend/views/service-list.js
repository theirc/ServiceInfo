var Backbone = require('backbone'),
    template = require("../templates/service-list.hbs"),
    i18n = require('i18next-client'),
    models = require('../models/service')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.services = new models.Services();
        this.render();
    },

    render: function() {
        var $el = this.$el;
        var services = this.services;
        this.services.fetch().then(function(r){
            window.services = services;
            var p = services.loadSubModels();
            p.then(function(){
                $el.html(template({
                    services: services.data(),
                }));
                $el.i18n();
            });
        });
    },

    events: {
    },
})
