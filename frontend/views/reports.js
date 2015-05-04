var Backbone = require('backbone'),
    template = require("../templates/reports.hbs")
;


module.exports = Backbone.View.extend({
    render: function() {
        this.$el.html(template({}));
    }
});
