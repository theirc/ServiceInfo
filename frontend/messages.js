var $ = require('jquery'),
    i18n = require('i18next-client'),
    template = require("./templates/message.hbs");

module.exports = {
    clear: function () {
        $('#messages').html('');
    },
    add: function (s) {
        /* Add string 's' to the messages in the message area */
        $('#messages').append(template({message: s}));
    },
    error: function (e) {
        /* Given the argument to a promise error function, report
           the problem in the message area.
        */
        console.error(e);
        if (e.status >= 500) {
            this.add(e.statusText);
        } else if (e.status >= 400) {
            this.add(e.responseText);
        } else {
            this.add(i18n.t('Global.UnknownError'));
        }
    }
};
