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
    Activate Materialize sliders.
  */
  $('.slider').slider({full_width: true});

  /*
    Activate custom show-hide code.
  */
  $('.child-activate').click(function () {
    var $this = $(this);

    $this
      .parent()
      .next('.child-item')
      .toggleClass('open')
    ;
  });

  /*
    Activate Materialize select inputs.
  */
  $('select').material_select();

  /*
    Adjust for IE 11.
  */
  if (!isNaN(getInternetExplorerVersion())) {
    $('body').addClass('InternetExplorer');
  }

  /*
    Bind to rating radio buttons.
  */
  $('#page-rating .stars label').click(function () {
    $('#captcha-modal').openModal();
  });

  /*
    Initialize calendar.
  */
  (function () {
    var $calendar = $('.fullcalendar');
    var key = $calendar.data('api-key');
    var id = $calendar.data('calendar-id');
    if (key && id) {
      $calendar.fullCalendar({
        googleCalendarApiKey: key
        , events: {
          googleCalendarId: id
        }
      });
    }
  })();

  /*
    Set up captcha callback.
  */
  window.__submit_captcha__ = function () {
    setTimeout(function () {
      $('#captcha-modal').closeModal();
      $('#page-rating').submit();
    }, 1500);
  }
});
