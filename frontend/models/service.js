var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');
var servicearea = require('./servicearea');


var Service = _base.BaseModel.extend({
    apiname: 'services',
    loadSubModels: function () {
        var self = this;
        var url = this.get('area_of_service');
        var area = new servicearea.ServiceArea({url: url});
        area.fetch().then(function(){
            self.servicearea = area;
            self._data.servicearea = area.data();
        });
    },
})

var Services = _base.BaseCollection.extend({
    model: Service,
})

module.exports = {
    Service: Service,
    Services: Services,
};
