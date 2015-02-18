var Backbone = require('backbone'),
    config = require('../config'),
    _base = require('./_base');


var User = _base.BaseModel.extend({
    apiname: 'users',
    loadSubModels: function () {
    },
})

var Users = _base.BaseCollection.extend({
    model: User,
})

module.exports = {
    User: User,
    Users: Users,
};
