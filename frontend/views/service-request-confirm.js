var Backbone = require('backbone'),
    template = require("../templates/service-request-confirm.hbs");

module.exports = Backbone.View.extend({
    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
        this.$el.i18n();
    },
})
