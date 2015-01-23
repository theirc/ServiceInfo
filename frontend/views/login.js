var Backbone = require('backbone'),
    template = require("../templates/login.hbs"),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
    },

    events: {
        "click button": function(ev) {
            ev.preventDefault();
            var formdata = new FormData(this.$el.find('form')[0]);
            console.log(this.$el.find('form')[0], formdata);
        }
    }
})
