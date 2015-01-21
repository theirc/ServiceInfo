"use strict";
var HomeView = require('./views/home');
var ProviderFormView = require('./views/provider-form');
var $ = require('jquery'),
    Backbone = require('backbone');

module.exports = Backbone.Router.extend({
    routes: {
        "": "home",
    },

    home: function() {
        var $el = $(document.querySelector('#page'));
        var view = new ProviderFormView({el: $el});
        view.render();
    },
})
