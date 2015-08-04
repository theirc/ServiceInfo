var Backbone = require('backbone'),
    _ = require('underscore'),
    $ = require('jquery'),
    template = require("../templates/reports.hbs"),
    resultsTemplate = require("../templates/stats-table.hbs"),
    hashtrack = require('hashtrack'),
    api = require('../api'),
    config = require('../config')
;

var isFloat = function(n){
    return typeof n === "number" && parseInt(n) !== n;
};

var ReportTableView = Backbone.View.extend({
    ratingReportTypes: ['qos', 'communication'], // all other reports are 'totals' reports

    initialize: function (options) {
        this.chartEl = $(options.chartEl);
        this.report = options.report;
        this.results = null;
        this.flotOptions = {
            series: {bars: {show: true,
                            barWidth: 0.6,
                            align: "center"}},
            grid: {hoverable: true},
            yaxis: {min: 0,
                    tickDecimals: 0}};
        this.chartEl.bind("plothover", function (event, pos, item) {
            if (item) {
                var yStart = item.datapoint[1],
                    yEnd = item.datapoint[2],
                    yValue = yStart - yEnd;
                if (isFloat(yValue)) {
                    // round floats to 2 decimals
                    yValue = yValue.toFixed(2);
                }
                $("#report-tooltip").html(yValue)
                    .css({top: pos.pageY, left: pos.pageX+25})
                    .show();
            } else {
                $("#report-tooltip").hide();
            }
        });
    },

    render: function () {
        var context = {loaded: false};
        if (this.results === null) {
            this.chartEl.hide();
            this.fetchReport();
        } else {
            context.loaded = true;
            context.headers = this.results.headers;
            context.rows = this.results.rows;
            this.chartEl.show();
            this.chartEl.plot(this.results.chartData, this.results.chartOptions);
        }

        this.$el.html(resultsTemplate(context));
        this.$el.i18n();
    },

    fetchReport: function () {
        api.request('GET', 'api/reports/' + this.report + '/')
            .then(_.bind(this.processReport, this));
    },

    isRatingReport: function() {
        return this.ratingReportTypes.indexOf(this.report) > -1;
    },

    processReport: function (data) {
        var lang = config.get('forever.language'),
            headers = null,
            rows = _.map(data, function (row) {
                var result = [row['name_' + lang] ];
                _.each(row.totals, function (total) {
                    result.push(total.total);
                });
                if (headers === null) {
                    headers = _.map(row.totals, function (total) {
                        return total['label_' + lang];
                    });
                }
                return result;
            }),
            chartData = [],
            ticks = [],
            chartOptions = this.flotOptions;

        if (this.isRatingReport()) {
            // Rating Report
            _.each(data, function (row) {
                var label = row['name_' + lang],
                    numRatings = 0,
                    sumOfRatings = 0,
                    avgRating = 0;
                _.each(row.totals, function (total) {
                    var rating = Number(total.label_en);
                    numRatings += total.total;
                    sumOfRatings += (total.total * rating);
                });
                if (numRatings !== 0) {
                    avgRating = sumOfRatings / numRatings;
                }
                chartData.push({'color': row.number,
                                'data': [[row.number, avgRating]]});
                ticks.push([row.number, label]);
            });
            // Set options specific to 'Rating' chart
            chartOptions.xaxis = {ticks: ticks};
            chartOptions.yaxis = {max: 5};
        } else {
            // Totals Report
            var stagger = 0,
                // the more groups there are, the thinner they are
                barWidth = 1.0 / (headers.length + 1);

            chartData = _.map(headers, function(header) {
                var values = [];
                _.each(data, function (row) {
                    var rows_with_this_header = _.filter(row.totals, function(total){
                        return total['label_' + lang] === header;
                    });
                    _.each(rows_with_this_header, function (total) {
                        // offset by 'stagger' so bar is just to right of previous bar
                        values.push([row.number + stagger, total.total]);
                        ticks.push([row.number, row['name_' + lang]]);
                    });
                });
                stagger += barWidth;
                return {'label': header, 'data': values};
            });
            chartOptions.xaxis = {ticks: ticks, color: '#f3f3f4'}; // matches background
            chartOptions.series.bars.barWidth = barWidth;
        }

        this.results = {
            headers: headers,
            rows: rows,
            chartData: chartData,
            chartOptions: chartOptions
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
            {value: 'wait-times', label: 'WaitTime'},
            {value: 'qos', label: 'QOS'},
            {value: 'failure', label: 'Failure'},
            {value: 'communication', label: 'Communication'},
            {value: 'num-services-by-provider-type', label: 'NumServicesByProviderType'},
            {value: 'num-services-by-service-type', label: 'NumServicesByServiceType'}
        ];
    },

    render: function () {
        var context = {
            options: _.map(this.reportOptions, function (option) {
                option.selected = option.value === this.report;
                return option;
            }, this)
        };
        this.$el.html(template(context));
        this.resultsView = new ReportTableView({
            el: '#report-table',
            chartEl: '#chart',
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
        var today = new Date(),
            filename = this.report + '-' + today.toISOString().replace(/\T.*$/, '') + '.csv';
        api.request('GET', 'api/servicetypes/' + this.report + '/?format=csv')
            .then(function (response) {
                var blob = new Blob([response], {type: 'text/csv'}),
                    blobURL, link;
                // Attempt to name the saved file
                // IE supports a native saveBlob
                // https://msdn.microsoft.com/en-us/library/windows/apps/hh441122.aspx
                if (navigator.msSaveBlob) {
                    navigator.msSaveBlob(blob, filename);
                } else {
                    // Fall back to download attribute if supported
                    link = document.createElement('a');
                    blobURL = window.URL.createObjectURL(blob);
                    if ('download' in link) {
                        // Use download attribute
                        link.style = 'display: none;';
                        link.href = blobURL;
                        link.download = filename;
                        document.body.appendChild(link);
                        link.click();
                    } else {
                        // Can't control the file name
                        window.location = blobURL;
                    }
                }
            });
    }
});
