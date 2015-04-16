"use strict";
var $ = require('jquery'),
    config = require('./config'),
    i18n = require('i18next-client'),
    Backbone = require('backbone'),
    messages = require('./messages')
;

var views = {
    "home": require('./views/home'),
    "register": require('./views/provider-form'),
    "register-confirm": require('./views/provider-form-confirm'),
    "register-changed": require('./views/provider-form-changed'),
    "account-activate": require('./views/account-activate'),
    "account-activation-failed": require('./views/account-activation-failed'),
    "account-resend-verification": require('./views/account-resend-verification'),
    "service": require('./views/service-form'),
    "feedback-form": require('./views/feedback-form'),
    "feedback-confirm": require('./views/feedback-confirm'),
    "map": require('./views/map'),
    "search-list": require('./views/search-list'),
    "service-cancel": require('./views/service-cancel'),
    "service-list": require('./views/service-list'),
    "service-detail": require('./views/service-detail'),
    "login": require('./views/login'),
    "password-reset": require('./views/password-reset'),
    "password-reset-form": require('./views/password-reset-form'),
    "admin": require('./views/admin'),
};

var view, viewName;

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
            viewName = name;
            if (!view.skip_initial_render) {
                i18n.init(function () {
                    view.render.apply(view, viewArguments);
                    view.$el.i18n({
                        lng: config.get('forever.language'),
                    });
                });
            }
            $('#menu-container').addClass("menu-closed");
            $('#menu-container').removeClass("menu-open");
        })
    }
}

module.exports = Backbone.Router.extend({
    initialize: function() {
        this.route(/search\/?/, loadPage("search-list"));
        this.route(/search\/map/, loadPage("map"));
        this.route(/feedback\/list/, loadPage("search-list", ['feedback']));
        this.route(/feedback\/map/, loadPage("map", ['feedback']));
    },
    routes: {
        "": loadPage("home"),
        "admin": loadPage("admin"),
        "register": loadPage("register"),
        "register/changed": loadPage("register-changed"),
        "register/confirm": loadPage("register-confirm"),
        "register/verify/:key": loadPage("account-activate", ['key']),
        "register/activation_failed": loadPage("account-activation-failed"),
        "register/resend_verification": loadPage("account-resend-verification"),
        "manage/service": loadPage("service"),
        "manage/service/:id": loadPage("service", ['id']),
        "manage/service/cancel/:id": loadPage("service-cancel", ['id']),
        "manage/service-list": loadPage("service-list"),

        "service/:id": loadPage("service-detail", ['id']),

        "feedback/confirm": loadPage("feedback-confirm"),
        "feedback/:id": loadPage("feedback-form", ['id']),

        "service/cancel/:id": loadPage("service-cancel", ['id']),
        "service-list": loadPage("service-list"),
        "login": loadPage("login"),
        "password-reset": loadPage("password-reset"),
        "password-reset-form": loadPage("password-reset-form"),
        "logout": function() {
            config.remove('forever.authToken');
            config.remove('forever.email');
            config.remove('forever.isStaff');
            $('.menu-item-staff').hide();
            window.location.hash = '';
            window.location.reload();
        },
    },
})
