var Backbone = require('backbone'),
    template = require("../templates/provider-form-changed.hbs"),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
        $el.i18n();
    },
})
