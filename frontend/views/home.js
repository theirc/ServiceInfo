var Backbone = require('backbone'),
    template = require("../templates/home.hbs"),
    i18n = require('i18next-client'),
    config = require('../config'),
    messages = require('../messages'),
    api = require('../api'),
    $ = require('jquery')
;


module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
        this.$el.i18n();
    },
})
