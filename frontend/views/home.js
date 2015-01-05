var Backbone = require('backbone'),
    template = require("../templates/home.hbs"),
    i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({name: "World"}));
        i18n.init(function(t){
            $el.i18n();
            console.log(t("test.hello"));
        })
    },
})
