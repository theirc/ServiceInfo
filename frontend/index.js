var $ = require('jquery');
window.jQuery = $;
require('jquery-form/jquery.form');
var Backbone = require('backbone');
Backbone.$ = require('jquery');
var underscore = require('underscore');
var config = require('./config');
var api = require('./api');
var i18n = require('i18next-client');
var hashtrack = require('hashtrack');
var _ = underscore;

// Load Flot: http://www.flotcharts.org/
require('Flot');

hashtrack.init();
require('es6-promise').polyfill();

var models = require('./models/models');

window.$ = $;
window.require = require;

var Router = require('./router');
var router = new Router();

$('body').on("click", ".back-button", function (event) {
    event.preventDefault();
    window.history.back();
});

$(function(){

    Backbone.history.start();

    $.ajaxSetup({
        beforeSend: function(xhr) {
            if (config.get('forever.authToken')) {
                xhr.setRequestHeader(
                    "ServiceInfoAuthorization",
                    "Token "+config.get('forever.authToken')
                );
            }
        }
    });

    var LangToggleView = require('./views/language-toggle');
    var lt = new LangToggleView({el: $('#language-toggle')});

    $("#menu-toggle").click(function() {
        $('#menu-container').toggleClass("menu-closed menu-open");
    });

    $('.menu-item-language').click(function() {
        lt.show();
        $('#menu-container').addClass("menu-closed");
        $('#menu-container').removeClass("menu-open");
    });
});
