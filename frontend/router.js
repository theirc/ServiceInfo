"use strict";
var $ = require('jquery'),
    Backbone = require('backbone');

var views = {
    "home": require('./views/home'),
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
        $('#menu-container').addClass("menu-closed");
        $('#menu-container').removeClass("menu-open");
    }
}

module.exports = Backbone.Router.extend({
    routes: {
        "": loadPage("home"),
        "register": loadPage("register"),
        "feedback": loadPage("feedback"),
        "map": loadPage("map"),
        "login": loadPage("login"),
    },
})
