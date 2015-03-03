var Backbone = require('backbone');
var config = require('../config');
var messages = require('../messages');
var _base = require('./_base');
var servicearea = require('./servicearea');
var servicetype = require('./servicetype');


var Service = _base.BaseModel.extend({
    apiname: 'services',
    loadSubModels: function () {
        var self = this;
        var area = new servicearea.ServiceArea({url: this.get('area_of_service')});
        var type = new servicetype.ServiceType({url: this.get('type')});

        var wait = [area.fetch(), type.fetch()];

        return new Promise(function(resolve, error) {
            Promise.all(wait).then(function(){
                self.attributes.servicearea = area;
                self.attributes.servicetype = type;

                resolve(self);
            }, function onerror(error) {
                messages.error(error);
            });
        });

    },

    data: function() {
        var data = _base.BaseModel.prototype.data.apply(this, arguments);
        data.isApproved = this.isApproved();
        data.isRejected = this.isRejected();
        if (this.attributes.servicearea) {
            data.servicearea = this.attributes.servicearea.data();
        }
        if (this.attributes.servicetype) {
            data.servicetype = this.attributes.servicetype.data();
        }
        return data;
    },

    isApproved: function() {
        return this.get('status') == 'current';
    },

    isRejected: function() {
        return this.get('status') == 'rejected';
    },
})

var Services = _base.BaseCollection.extend({
    model: Service,

    loadSubModels: function () {
        var p = [];
        $.each(this.models, function() {
            p.push(this.loadSubModels());
        });
        return Promise.all(p);
    },
})

module.exports = {
    Service: Service,
    Services: Services,
};
