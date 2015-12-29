var $ = window.jQuery;

function init (id, lg, urls, editing) {
  /*
    Custom functionality for the language picker modal:

    * Checks for forever.language value on localStorage on page load. If
      not found, opens the modal.
    * On clicking modal link, sets forever.language on localStorage before
      navigating to new page.
  */

  var app_lg;
  var no_redirect = localStorage.getItem('no_redirect');
  var $lp = $(id);

  if (no_redirect) {
    localStorage.removeItem('no_redirect');
  }

  $lp.click(function (e) {
    /*
      Delegated event listener to watch for clicks on modal link.
    */
    var lg;

    e.preventDefault();

    if (lg = $(e.target).data('lang')) {
      localStorage.setItem('forever.language', JSON.stringify(lg));
    }

    window.location.href = e.target.href;
  });

  if (!(app_lg = JSON.parse(localStorage.getItem('forever.language')))) {
    $lp.openModal();
  } else if (app_lg !== lg && !no_redirect && !editing) {
    localStorage.setItem('no_redirect', true);
    window.location.href = urls[app_lg];
  }
}

module.exports = init;
