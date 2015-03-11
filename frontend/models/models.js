var _base = require('./_base');

module.exports = {
    service: require('./service'),
    servicearea: require('./servicearea'),
    servicetype: require('./servicetype'),
    provider: require('./provider'),
    providertype: require('./providertype'),
    user: require('./user'),
    preload: _base.preload,
    preloaded: _base.preloaded,
};
