"use strict";
var $ = require('jquery'),
    config = require('./config'),
    i18n = require('i18next-client'),
    Backbone = require('backbone')
;

var views = {
    "register": require('./views/provider-form'),
    "register-confirm": require('./views/provider-form-confirm'),
    "account-activate": require('./views/account-activate'),
    "service": require('./views/service-form'),
    "feedback": require('./views/feedback'),
    "map": require('./views/map'),
    "service-list": require('./views/service-list'),
    "login": require('./views/login'),
};

function loadPage(name, params) {
    return function() {
        config.ready(function(){
            var $el = $(document.querySelector('#page'));
            var opts = {
                el: $el
            };
            var params = params || [];
            for (var i=0; i < params.length; i++) {
                opts[params[i]] = arguments[i];
            }
            var view = new views[name](opts);
            view.render.apply(view, arguments);
            i18n.init(function(){
                view.$el.i18n({
                    lng: config.get('lang'),
                });
            });
            $('#menu-container').addClass("menu-closed");
            $('#menu-container').removeClass("menu-open");
        })
    }
}

module.exports = Backbone.Router.extend({
    routes: {
        "": function() {
            if (config.get('forever.authToken')) {

            } else {

            }
        },
        "register": loadPage("register"),
        "register/confirm": loadPage("register-confirm"),
        "register/verify/:key": loadPage("account-activate", ['key']),
        "service": loadPage("service"),
        "feedback": loadPage("feedback"),
        "map": loadPage("map"),
        "service-list": loadPage("service-list"),
        "login": loadPage("login"),
        "logout": function() {
            config.remove('forever.authToken');
            window.location.hash = '';
            window.location.reload();
        },
    },
})
