"use strict";
var HomeView = require('./views/home');
var $ = require('jquery'),
    Backbone = require('backbone');

module.exports = Backbone.Router.extend({
    routes: {
        "": "home",
    },

    home: function() {
        var $el = $(document.querySelector('#application'));
        var view = new HomeView({el: $el});
        view.render();
    },
})
