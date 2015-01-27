"use strict";
var $ = require('jquery'),
    config = require('./config'),
    i18n = require('i18next-client'),
    Backbone = require('backbone')
;

var views = {

    "register": require('./views/provider-form'),
    "feedback": require('./views/feedback'),
    "map": require('./views/map'),
    "login": require('./views/login'),
};

function loadPage(name) {
    return function() {
        var $el = $(document.querySelector('#page'));
        var view = new views[name]({el: $el});
        view.render();
        i18n.init(function(){
            view.$el.i18n({
                lng: config.get('lang'),
            });
        });
        $('#menu-container').addClass("menu-closed");
        $('#menu-container').removeClass("menu-open");
    }
}

module.exports = Backbone.Router.extend({
    routes: {
        
        "register": loadPage("register"),
        "feedback": loadPage("feedback"),
        "map": loadPage("map"),
        "login": loadPage("login"),
    },
})
