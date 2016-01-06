var language_picker = window.language_picker = require('./language-picker.js');

function getInternetExplorerVersion () {
//http://stackoverflow.com/questions/17907445/how-to-detect-ie11
  var rv = NaN;

  if (navigator.appName === 'Microsoft Internet Explorer') {
    var ua = navigator.userAgent;
    var re = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null) {
      rv = parseFloat( RegExp.$1 );
    }
  } else if (navigator.appName === 'Netscape') {
    var ua = navigator.userAgent;
    var re = new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null) {
      rv = parseFloat( RegExp.$1 );
    }
  }

  return rv;
}

jQuery(function ($) {
  /*
    Activate Materialize mobile menu.
  */
  $(".button-collapse").sideNav();

  /*
    Activate Materialize dropdowns.
  */
  $(".dropdown-button").each(function () {
    $(this).dropdown();
  });

  /*
    Activate Materialize modals.
  */
  $('.modal-trigger').leanModal();

  /*
    Activate Materialize parallax.
  */
  if (!$('.cms-toolbar-expanded').length) {
    $('.parallax').parallax();
  }

  /*
    Adjust for IE 11.
  */
  if (!isNaN(getInternetExplorerVersion())) {
    $('body').addClass('InternetExplorer');
  }

  /*
    Ensure that submenus with active children are open on page load.
    Easiest way to do this: trigger the 'click' behavior on the containing
    collapsible elements.
  */
  $('#nav .collapsible-body, #mobile-menu .collapsible-body')
    .find('li.page-active')
    .parents('#nav li, #mobile-menu li')
    .children('.collapsible-header')
    .each(function () {
      $(this).trigger('click');
    })
  ;
});
