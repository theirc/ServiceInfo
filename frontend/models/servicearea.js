var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var ServiceArea = _base.BaseModel.extend({
    apiname: 'serviceareas',
})

var ServiceAreas = _base.BaseCollection.extend({
    model: ServiceArea,
})

_base.preload("servicearea", ServiceAreas);

module.exports = {
    ServiceArea: ServiceArea,
    ServiceAreas: ServiceAreas,
};
