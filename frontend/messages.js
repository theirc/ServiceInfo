var $ = require('jquery'),
    i18n = require('i18next-client'),
    template = require("./templates/message.hbs");

module.exports = {
    clear: function () {
        var $app = $('#application');
        var $msg = $('#messages');
        var $doc = $(document);
        var app_margin_top = $app.css('margin-top');
        $app.css({
            'margin-top': (app_margin_top - $msg.outerHeight()) + 'px'
        });
        $doc.scrollTop($doc.scrollTop() - $msg.outerHeight());
        $msg.html('');
    },
    add: function (s) {
        var $app = $('#application');
        var $msg = $('#messages');
        var $doc = $(document);
        var app_margin_top = $app.css('margin-top');
        /* Add string 's' to the messages in the message area */
        $msg.append(template({message: s}));
        $app.css({
            'margin-top': ($msg.outerHeight() + app_margin_top) + 'px'
        });
        $doc.scrollTop($doc.scrollTop() + $msg.outerHeight());
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
    },
    log_messages: function (d) {
        /* Given a dictionary of field names and errors, log them
        all
         */
        var self = this;
        $.each(d, function(k) {
            self.add(k + ": " + d[k]);
        });
    }
};
