var Backbone = require('backbone'),
    template = require("../templates/home.hbs");

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        this.$el.html(template({name: "World"}));
    },
})
