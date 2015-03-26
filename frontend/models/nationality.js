var Backbone = require('backbone');
var config = require('../config');
var _base = require('./_base');


var Nationality = _base.BaseModel.extend({
    apiname: 'nationality'
})

var Nationalities = _base.BaseCollection.extend({
    model: Nationality
})

_base.preload("nationality", Nationalities);

module.exports = {
    Nationality: Nationality,
    Nationalities: Nationalities
};
