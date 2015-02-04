var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var Service = _base.BaseModel.extend({
    apiname: 'services',
})

var Services = _base.BaseCollection.extend({
    model: Service,
})

module.exports = {
    Service: Service,
    Services: Services,
};
