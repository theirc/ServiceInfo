var $ = require('jquery');
var menu = require('../config').components.menu;

function init () {
    $(menu.toggle).click(function() {
        $(menu.container).toggleClass([menu.closed_class, menu.open_class].join(' '));
    });
}

module.exports = init;
