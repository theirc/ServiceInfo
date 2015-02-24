var Backbone = require('backbone');
var config = require('../config');
var api = require('../api');


var debabelize = function debabelize(data, lang1, lang2, lang3) {
    /* Given a dictionary where some fields are repeated in different
    languages with keys like 'foo_en', 'foo_ar', and 'foo_fr', return
    a copy of the dictionary, with a single field 'foo' for each of the
    fields that had multiple languages, containing the value for lang1,
    or lang2 if lang1 is blank or missing, or lang3 if not lang2...
     */
    var out = {}, keys = Object.keys(data),
        i, key, name, name1, name2, name3;

    for (i = 0; i < keys.length; i += 1) {
        name = keys[i];
        if (name.indexOf('_en') > 0 || name.indexOf('_ar') > 0 || name.indexOf('_fr') > 0) {
            key = name.split('_')[0];
            if (!out[key]) {
                name1 = key + '_' + lang1;
                name2 = key + '_' + lang2;
                name3 = key + '_' + lang3;
                out[key] = data[name1] || data[name2] || data[name3];
            }
        } else {
            out[name] = data[name];
        }
    }
    return out;
};

var BaseModel = Backbone.Model.extend({
    initialize: function() {
        this._data = {};
    },

    url: function() {
        var url = this.get('url');
        if (!url) {
            var url = api.getAPIPrefix() + 'api/'+ this.__proto__.apiname +'/';
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
        /* Return a dictionary with the debabelized data from this model instance */
        var data;
        var lang1 = config.get('forever.language');
        var lang2, lang3;
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
        if (!this.attributes) { return {}; }
        data = debabelize(this.attributes, lang1, lang2, lang3);
        if (data.hasOwnProperty('selection_criteria')) {
            var old_criteria = data.selection_criteria;
            var new_criteria = [];
            for (var i = 0; i < old_criteria.length; i += 1) {
                if (old_criteria[i]) {
                    new_criteria.push(debabelize(old_criteria[i], lang1, lang2, lang3))
                }
            }
            data.selection_criteria = new_criteria;
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
        var url = api.getAPIPrefix() + 'api/'+ this.model.prototype.apiname +'/';
        return url;
    },

    parse: function(resp) {
        return resp;
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
