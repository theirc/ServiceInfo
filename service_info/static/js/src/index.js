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
});
