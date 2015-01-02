var $ = require('jquery');
var Backbone = require('backbone');
Backbone.$ = require('jquery');
var handlebars = require('handlebars');
var underscore = require('underscore');
var _ = underscore;

window.$ = $;

var Router = require('./router');
var router = new Router();

$('body').on("click", ".back-button", function (event) {
    event.preventDefault();
    window.history.back();
});

$(function(){
    Backbone.history.start();
});
