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
});
