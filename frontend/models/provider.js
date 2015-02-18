var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var Provider = _base.BaseModel.extend({
    apiname: 'providers',
    loadSubModels: function () {
    },
})

var Providers = _base.BaseCollection.extend({
    model: Provider,
})

module.exports = {
    Provider: Provider,
    Providers: Providers,
};
