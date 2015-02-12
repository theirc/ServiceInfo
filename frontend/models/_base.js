var Backbone = require('backbone');
var config = require('../config');

var BaseModel = Backbone.Model.extend({
    initialize: function() {
        this._data = {};
    },

    url: function() {
        var url = this.get('url');
        if (!url) {
            var url = config.get('api_location') + 'api/'+ this.__proto__.apiname +'/';
            var id = this.get('id');
            if (id) {
                url = url + id + '/';
            }
        }

        return url;
    },

    get: function(prop) {
        var value = Backbone.Model.prototype.get.call(this, prop);
        if (typeof value === 'undefined') {
            var lang = config.get('forever.language');
            var tvalue = Backbone.Model.prototype.get.call(this, prop + '_' + lang);
            if (tvalue) {
                return tvalue;
            }
        }
        return value;
    },

    data: function() {
        var data = this._data;
        var key;
        var lang1 = config.get('forever.language');
        var lang2, lang3, name1, name2, name3;
        if (lang1 === 'en') {
           lang2 = 'ar';
           lang3 = 'fr';
        } else if (lang1 === 'ar') {
           lang2 = 'en';
           lang3 = 'fr';
        } else {
           lang2 = 'en';
           lang3 = 'ar';
        }
        for (var name in this.attributes) {
            if (name.indexOf('_en') > 0 || name.indexOf('_ar') > 0 || name.indexOf('_fr') > 0) {
                key = name.split('_')[0];
                if (! data[key]) {
                   name1 = key + '_' + lang1;
                   name2 = key + '_' + lang2;
                   name3 = key + '_' + lang3;
                   data[key] = this.get(name1) || this.get(name2) || this.get(name3);
                }
            } else {
               data[name] = this.get(name);
            }
        }
        data['id'] = this.get('id');
        return data;
    },
});

var BaseCollection = Backbone.Collection.extend({
    loadSubModels: function() {
        for (var i=0; i < this.models.length; i++) {
            this.models[i].loadSubModels();
        }
    },

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
            data.push(this.models[i].data());
        }
        return data;
    },
});

module.exports = {
    BaseModel: BaseModel,
    BaseCollection: BaseCollection,
};
