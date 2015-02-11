var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var ProviderType = _base.BaseModel.extend({
    apiname: 'providertypes',
})

var ProviderTypes = _base.BaseCollection.extend({
    model: ProviderType,
})

module.exports = {
    ProviderType: ProviderType,
    ProviderTypes: ProviderTypes,
};
