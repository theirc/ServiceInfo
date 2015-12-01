var $ = require('jquery');
window.jQuery = $;
window.$ = $;
var lt = require('../config').components.language_toggle;

function init () {
  var $toggle = $(lt.root);
  var $shower = $(lt.shower);

  function show () {
    var curPos = $toggle.position();
    $toggle
      .css('visibility', 'hidden')
      .removeClass('hidden')
      .css({
          top: 'auto'
          , left: 'auto'
      })
      ;

    var anim = $toggle.position();

    $toggle
      .addClass('hidden')
      .css(curPos)
      .css('visibility', 'visible')
      .animate(anim, {duration: 0.5, complete: function () {
          $toggle.css({
              top: '0px'
              , left: 'auto'
          });
      }})
      .removeClass('hidden')
      ;
      
    setTimeout(function () {
        $toggle.removeClass('no-animate');
    }, 0);
  }

  $shower.click(function (e) {
    e.preventDefault();
    show();
  });
}

module.exports = init;
