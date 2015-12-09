var $ = require('jquery');
var menu = require('../config').components.menu;

function init () {
    $(menu.toggle).click(function() {
        $(menu.container).toggleClass([menu.closed_class, menu.open_class].join(' '));
    });

    $(menu.parent_items).click(function (e) {
        var $this = $(this);
        var $others;
        e.preventDefault();
        console.log(e);
        $this.parent().toggleClass('active');
        $this.next('ul').slideToggle({
            duration: 200
        });

        /*
            Close drop-down menus that aren't this one
            or the parent of this one.
        */
        $others = $('#menu > li.parent')
            .not($this.closest('#menu > li.parent'));
        $others.removeClass('active');
        $others.find('ul').first()
            .slideUp({
                duration: 200
            })
        ;
    });
}

module.exports = init;
