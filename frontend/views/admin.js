/* View to go to the Django admin */
var Backbone = require('backbone'),
    api = require('../api')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        window.location = api.getAPIPrefix() + 'admin/';
    }
})
