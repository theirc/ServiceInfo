var $ = require('jquery');
var page = require('../config').components.page;
var footer = require('../config').components.footer;

/*
  On the CMS, the footer needs to be allowed to grow arbitrarily tall.
  The problem with this is that the page well also needs to have its bottom
  padding adjusted to match the height of the footer.

  The solution is to re-pad the content well on page load and whenever the
  window is resized or reoriented.
*/

function init () {
  var $page = $(page.container);
  var $footer = $(footer.container);

  resize($page, $footer);

  $(window).on('resize reorient', function () { resize($page, $footer); });
}

function resize ($page, $footer) {
  $page.css({
    'padding-bottom': $footer.outerHeight() + 'px'
  });
}

module.exports = init;
