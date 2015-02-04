var Backbone = require('backbone');
var config = require('../config');

var BaseModel = Backbone.Model.extend({
    url: function() {
        var url = config.get('api_location') + 'api/'+ this.__proto__.apiname +'/';
        var id = this.get('id');
        if (id) {
            url = url + id + '/';
        }
        return url;
    },

    get: function(prop) {
        var value = Backbone.Model.prototype.get.call(this, prop);
        if (typeof value === 'undefined') {
            var tvalue = Backbone.Model.prototype.get.call(this, prop + '_' + config.get('lang'));
            if (tvalue) {
                return tvalue;
            }
        }
        return value;
    },

    data: function() {
        var data = {};
        var key;
        for (var name in this.attributes) {
            if (name.indexOf('_en') > 0) {
                key = name.split('_')[0];
            } else {
                key = name;
            }
            data[key] = this.get(name);
        }
        return data;
    },
});

var BaseCollection = Backbone.Collection.extend({
    url: function() {
        var url = config.get('api_location') + 'api/'+ this.model.prototype.apiname +'/';
        return url;
    },

    parse: function(resp) {
        return resp.results;
    },

    data: function() {
        var data = [];
        for (var i=0; i < this.models.length; i++) {
            window.a_thing = this.models[i];
            data.push(this.models[i].data());
        }
        return data;
    },
});

module.exports = {
    BaseModel: BaseModel,
    BaseCollection: BaseCollection,
};
