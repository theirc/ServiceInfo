var Backbone = require('backbone'),
    _ = require('underscore'),
    template = require("../templates/reports.hbs"),
    resultsTemplate = require("../templates/stats-table.hbs"),
    hashtrack = require('hashtrack'),
    api = require('../api'),
    config = require('../config')
;

var ReportTableView = Backbone.View.extend({

    initialize: function (options) {
        this.report = options.report;
        this.results = null;
    },

    render: function () {
        var context = {loaded: false};
        if (this.results === null) {
            this.fetchReport();
        } else {
            context.loaded = true;
            context.headers = this.results.headers;
            context.rows = this.results.rows;
        }
        this.$el.html(resultsTemplate(context));
        this.$el.i18n();
    },

    fetchReport: function () {
        api.request('GET', 'api/servicetypes/' + this.report + '/')
            .then(_.bind(this.processReport, this));
    },

    processReport: function (data) {
        var lang = config.get('forever.language'),
            headers = null,
            rows = _.map(data, function (row) {
                var result = [row['name_' + lang], ];
                _.each(row.totals, function (total) {
                    result.push(total.total);
                })
                if (headers === null) {
                    headers = _.map(row.totals, function (total) {
                        return total['label_' + lang];
                    });
                }
                return result;
            });
        this.results = {
            headers: headers,
            rows: rows
        };
        this.render();
    }
});


module.exports = Backbone.View.extend({
    events: {
        'change :input[name="stat"]': 'updateReport',
        'click .download': 'downloadReport'
    },

    initialize: function () {
        this.report = hashtrack.getVar('stat') || 'wait-times';
        this.reportOptions = [
            {value: 'wait-times', label: 'WaitTime'}
        ];
    },

    render: function () {
        var context = {
            options: _.map(this.reportOptions, function (option) {
                option.selected = option.value == this.report;
                return option;
            }, this)
        };
        this.$el.html(template(context));
        this.resultsView = new ReportTableView({
            el: '#report-table',
            report: this.report
        });
        this.resultsView.render();
    },

    updateReport: function (e) {
        if (this.resultsView) {
            this.resultsView.remove();
        }
        hashtrack.setVar('stat', e.target.value);
    },

    downloadReport: function (e) {
        e.preventDefault();
        api.request('GET', 'api/servicetypes/' + this.report + '/?format=csv')
            .then(function (response) {
                var blob = new Blob([response], {type: 'text/csv'});
                window.location = window.URL.createObjectURL(blob);
            });
    }
}); 
