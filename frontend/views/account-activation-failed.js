var account_activation_failed_template = require("../templates/account-activation-failed.hbs"),
    resend_verification = require('./account-resend-verification')
;

module.exports = resend_verification.extend({
    template: account_activation_failed_template
});
