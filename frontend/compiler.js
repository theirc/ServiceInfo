var handlebars = require('hbsfy/runtime');

handlebars.registerHelper({
        toLowerCase: function(str) {
            return str.toLowerCase();
        },
        multiline: function (s) {
            var s2 = handlebars.escapeExpression(s).replace(/\n/g, '<br>');
            return new handlebars.SafeString(s2);
        }
    });

module.exports = handlebars;
