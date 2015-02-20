/* View to go to the Django admin */
var Backbone = require('backbone'),
    config = require('../config')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        window.location = config.get('api_location') + 'admin/';
    }
})
