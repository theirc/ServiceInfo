var Backbone = require('backbone');
var config = require('../config');
var messages = require('../messages');
var _base = require('./_base');
var servicearea = require('./servicearea');
var servicetype = require('./servicetype');
var provider = require('./provider');
var api = require('../api');


var Service = _base.BaseModel.extend({
    apiname: 'services',
    loadSubModels: function () {
        var self = this;
        var area = new servicearea.ServiceArea({url: this.get('area_of_service')});
        var type = new servicetype.ServiceType({url: this.get('type')});
        var provider_fetch_url = api.getAbsoluteAPIURL(this.get('provider_fetch_url'));
        var provider_fetch = new provider.Provider({url: provider_fetch_url});

        var wait = [area.fetch(), type.fetch(), provider_fetch.fetch()];

        return new Promise(function(resolve, error) {
            Promise.all(wait).then(function(){
                self.attributes.servicearea = area;
                self.attributes.servicetype = type;
                self.attributes.provider = provider_fetch;

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
        window.service = this;
        if (typeof this.attributes.servicearea !== 'undefined') {
            if (typeof this.attributes.servicearea.data === 'function') {
                data.servicearea = this.attributes.servicearea.data();
            }
        }
        if (typeof this.attributes.servicetype !== 'undefined') {
            if (typeof this.attributes.servicetype.data === 'function') {
                data.servicetype = this.attributes.servicetype.data();
            }
        }
        if (typeof this.attributes.provider !== 'undefined') {
            if (typeof this.attributes.provider.data === 'function') {
                data.provider = this.attributes.provider.data();
            }
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

var PublicServices = Services.extend({
    url: function() {
        var url = api.getAPIPrefix() + 'api/'+ this.model.prototype.apiname +'/search/';
        return url;
    },
})

module.exports = {
    Service: Service,
    Services: Services,
    PublicServices: PublicServices,
};
