var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var Provider = _base.BaseModel.extend({
    apiname: 'providers',
    loadSubModels: function () {
    },
})

var _providerCache = {};
var Providers = _base.BaseCollection.extend({
    model: Provider,
})

module.exports = {
    Provider: Provider,
    Providers: Providers,

    fetchAndCache: function(url) {
        if (_providerCache[url]) {
            provider = _providerCache[url];
            return new Promise(function(resolve, error) {
                resolve(provider);
            });
        } else {
            var provider = new Provider({url: url});
            return new Promise(function(resolve, error) {
                _providerCache[url] = provider;
                provider.fetch().then(function() {
                    resolve(provider);
                }, error);
            });
        }
    },
};
