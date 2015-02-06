var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var ServiceType = _base.BaseModel.extend({
    apiname: 'servicetypes',
})

var ServiceTypes = _base.BaseCollection.extend({
    model: ServiceType,
})

module.exports = {
    ServiceType: ServiceType,
    ServiceTypes: ServiceTypes,
};
