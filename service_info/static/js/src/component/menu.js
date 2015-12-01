var $ = require('jquery');
window.jQuery = $;
window.$ = $;

var menu = require('../config').components.menu;

function init () {
    $(menu.toggle).click(function() {
        $(menu.container).toggleClass([menu.closed_class, menu.open_class].join(' '));
    });

    $(menu.top_items).click(function (e) {
        e.preventDefault();
        console.log(e);
        $(this).toggleClass('active');
        $(this).next('ul').slideToggle({
            duration: 200
        });
    });
}

module.exports = init;
