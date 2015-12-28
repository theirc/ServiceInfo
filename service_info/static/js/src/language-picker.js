var $ = window.jQuery;

function init (id) {
  /*
    Custom functionality for the language picker modal:

    * Checks for forever.language value on localStorage on page load. If
      not found, opens the modal.
    * On clicking modal link, sets forever.language on localStorage before
      navigating to new page.
  */

  var $lp = $(id);

  $lp.click(function (e) {
    /*
      Delegated event listener to watch for clicks on modal link.
    */
    var lg;

    e.preventDefault();

    if (lg = $(e.target).data('lang')) {
      localStorage.setItem('forever.language', lg);
    }

    window.location.href = e.target.href;
  });

  if (!localStorage.getItem('forever.language')) {
    $lp.openModal();
  }
}

module.exports = init;
