var $ = require('jquery');
var menu = require('../config').components.menu;

function init () {
    $(menu.toggle).click(function() {
        $(menu.container).toggleClass([menu.closed_class, menu.open_class].join(' '));
    });

    $(menu.parent_items).click(function (e) {
        e.preventDefault();
        console.log(e);
        $(this).toggleClass('active');
        $(this).parent().toggleClass('active');
        $(this).next('ul').slideToggle({
            duration: 200
        });
    });
}

module.exports = init;
