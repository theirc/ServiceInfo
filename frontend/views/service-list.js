var Backbone = require('backbone'),
    config = require('../config'),
    template = require("../templates/service-list.hbs"),
    i18n = require('i18next-client'),
    messages = require('../messages'),
    models = require('../models/service')
;

module.exports = Backbone.View.extend({
    initialize: function(){
        this.services = new models.Services();
        this.render();

        /* Render again if language changes */
        var $el = this.$el;
        var self = this;
        config.change("forever.language", function() {
            var detached = $('table#service-status').length === 0;
            if (detached) {
                config.unbind("forever.language", arguments.callee);
            } else {
                self.render();
            }
        });

        this.sort_order_by_status = {
            'current': '0',
            'draft': '1',
            'rejected': '2',
            'canceled': '2',
            'archived': '3'
        };
    },

    render: function() {
        messages.clear();
        var self = this;
        var $el = this.$el;
        var services = this.services;
        this.services.fetch().then(function(r){
            var no_services = services.length === 0;
            var p = services.loadSubModels();
            p.then(function(){
                var records = services.data(),
                    top_level = [],  // top-level records have no parent
                    by_id = {},  // index records by their ids.
                    parent_id,
                    i, j;

                var sort_func = function (a, b) {
                    return a.order > b.order;
                };

                for (i = 0; i < records.length; i++) {
                    // arrange so we can find a record by its id in the next loop
                    by_id[records[i].id] = records[i];
                    // every record has a list of its children
                    records[i].children = [];  // collect a record's children here (updates to it)
                }

                for (i = 0; i < records.length; i++) {
                    records[i].is_draft = records[i].status === 'draft';
                    records[i].is_rejected = records[i].status === 'rejected';
                    records[i].is_current = records[i].status === 'current';
                    records[i].is_update = ! records[i].is_current;
                    if (records[i].update_of) {
                        parent_id = parseInt(records[i].update_of.match(/(\d+)\/$/)[1]);
                        records[i].parent = by_id[parent_id];
                    }
                    if (records[i].parent === undefined) {
                        top_level.push(records[i]);
                    } else {
                        records[i].parent.children.push(records[i]);
                    }

                    // our sorts will order by status, then name
                    records[i].order = self.sort_order_by_status[records[i].status] + records[i].name;
                }

                // sort top-level records by status then name
                top_level.sort(sort_func);
                // also sort records' children
                // And figure out which records can be updated
                // And put our records in a single list again, with a traversal of our shallow tree
                records = [];
                for (i = 0; i < top_level.length; i++) {
                    var top = top_level[i], children = top.children;
                    records.push(top);
                    children.sort(sort_func);
                    top.can_update = (top.status === 'current');
                    for (j = 0; j < children.length; j++) {
                        var child = children[j];
                        // if a child is a draft, then we can update it, not its parent
                        child.can_update = (child.status === 'draft');
                        if (child.can_update) {
                            top.can_update = false;
                        }
                        records.push(top_level[i].children[j]);
                    }
                }

                $el.html(template({
                    services: records,
                    no_services: no_services,
                }));
                $el.i18n();
            }, function onerror(e) {
                messages.error(e);
            });
        }, function onerror(e) {
            messages.error(e);
        });
    },

    events: {
    },
})
