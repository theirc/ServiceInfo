var Backbone = require('backbone'),
    _ = require('underscore'),
    template = require("../templates/reports.hbs"),
    hashtrack = require('hashtrack')
;


module.exports = Backbone.View.extend({
    events: {
        'change :input[name="stat"]': 'updateReport'
    },

    initialize: function () {
        this.report = hashtrack.getVar('stat') || 'wait-times';
        this.reportOptions = [
            {value: 'wait-times', label: 'WaitTime'}
        ];
    },

    render: function() {
        var context = {
            options: _.each(this.reportOptions, function (option) {
                option.selected = option.value == this.report;
                return option;
            }, this)
        };
        this.$el.html(template(context));
    },

    updateReport: function (e) {
        hashtrack.setVar('stat', e.target.value);
    }
}); 
