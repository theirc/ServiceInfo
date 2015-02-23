"use strict";
var $ = require('jquery'),
    config = require('./config'),
    i18n = require('i18next-client'),
    Backbone = require('backbone'),
    messages = require('./messages')
;

var views = {
    "register": require('./views/provider-form'),
    "register-confirm": require('./views/provider-form-confirm'),
    "register-changed": require('./views/provider-form-changed'),
    "account-activate": require('./views/account-activate'),
    "service": require('./views/service-form'),
    "feedback": require('./views/feedback'),
    "map": require('./views/map'),
    "service-cancel": require('./views/service-cancel'),
    "service-list": require('./views/service-list'),
    "login": require('./views/login'),
    "password-reset": require('./views/password-reset'),
    "password-reset-form": require('./views/password-reset-form'),
    "admin": require('./views/admin')
};

var view;

function loadPage(name, params) {
    var params = params || [];

    return function() {
        messages.clear();
        var viewArguments = Array.prototype.slice.apply(arguments);
        config.ready(function(){
            var $el = $(document.querySelector('#page'));
            var opts = {
                el: $el
            };
            for (var i=0; i < params.length; i++) {
                opts[params[i]] = viewArguments[i];
            };
            if (view) {
                view.undelegateEvents();
            }
            view = new views[name](opts);
            i18n.init(function(){
                view.render.apply(view, viewArguments);
                view.$el.i18n({
                    lng: config.get('forever.language'),
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
        "admin": loadPage("admin"),
        "register": loadPage("register"),
        "register/changed": loadPage("register-changed"),
        "register/confirm": loadPage("register-confirm"),
        "register/verify/:key": loadPage("account-activate", ['key']),
        "service": loadPage("service"),
        "service/:id": loadPage("service", ['id']),
        "feedback": loadPage("feedback"),
        "map": loadPage("map"),
        "service/cancel/:id": loadPage("service-cancel", ['id']),
        "service-list": loadPage("service-list"),
        "login": loadPage("login"),
        "password-reset": loadPage("password-reset"),
        "password-reset-form": loadPage("password-reset-form"),
        "logout": function() {
            config.remove('forever.authToken');
            config.remove('forever.email');
            config.set('forever.isStaff', false);
            $('.menu-item-staff').hide();
            window.location.hash = '';
            window.location.reload();
        },
    },
})
