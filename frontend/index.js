var $ = require('jquery');
var Backbone = require('backbone');
Backbone.$ = require('jquery');
var handlebars = require('handlebars');
var underscore = require('underscore');
var config = require('./config');
var api = require('./api');
var _ = underscore;

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
                    "Authorization",
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
    })
});
