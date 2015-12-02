var $ = require('jquery');
window.jQuery = $;
window.$ = $;

/*
  UI COMPONENTS
*/

/*
  Mobile menu show/hide
*/
require('./component/menu')();
require('./component/language-toggle')();

/*
  Set up footer
*/
require('./component/footer')();

/*
  Initializing Google Analytics
*/
require('../../../../frontend/google-analytics.js')();
