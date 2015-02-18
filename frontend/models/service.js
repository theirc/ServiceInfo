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
                self.servicearea = area;
                self._data.servicearea = area.data();
                self.type = type;
                self._data.servicetype = type.data();

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
