var config_data = {
    'forever.language': 'en',
    'forever.isStaff': false
};
var has_been_set = {};
var _loaded = false;
var _pending = [];

var config = module.exports = {
    get: function(key) {
        return config_data[key];
    },
    set: function(key, value) {
        config_data[key] = value;
        has_been_set[key] = true;
        if (key.indexOf('forever.') === 0) {
            localStorage[key] = JSON.stringify(value);
        }
        this._triggerChange(key, 'set', value);
    },
    isset: function(key) {
        // Whether 'key' has ever been .set, meaning either it
        // was found in localStorage or .set has been called for
        // it after the config was initialized.  Basically means
        // we have a known preference and aren't just using a
        // default value.
        return has_been_set.hasOwnProperty(key);
    },
    remove: function(key) {
        if (config_data.hasOwnProperty(key)) {
            delete config_data[key];
        }
        localStorage.removeItem(key);
        this._triggerChange(key, 'remove');
    },

    change: function(key, cb) {
        if (typeof this._changeHandlers[key] === 'undefined') {
            this._changeHandlers[key] = [];
        }
        this._changeHandlers[key].push(cb);
    },
    unbind: function(key, cb) {
        if (typeof this._changeHandlers[key] !== 'undefined') {
            for (var i=0; i < this._changeHandlers[key].length; i++) {
                if (cb === this._changeHandlers[key][i]) {
                    this._changeHandlers[key].splice(i, 1);
                    break;
                }
            }
        }
    },
    _changeHandlers: {},
    _triggerChange: function(key) {

        if (key in this._changeHandlers) {
            for (var i=0; i < this._changeHandlers[key].length; i++) {
                this._changeHandlers[key][i].apply(this, arguments)
            }
        }
    },

    ready: function(cb) {
        var $this = this;
        if (!_loaded) {
            _pending.push(function() {
                cb.call($this);
            })
        } else {
            cb.call(this);
        }
    },
}

// Immediately treat saved values as set
for (var key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
        has_been_set[key] = true;
    }
}

var $ = require('jquery');
$(function($){
    var config_url = './config.json';
    $.getJSON(config_url, function(data) {
        $.extend(config_data, data);
        // "forever" config values are stored as JSON in local storage
        for (var key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                try {
                    config.set(key, JSON.parse(localStorage[key]));
                } catch (e) {
                    // when this fix first rolls out, users will have non-json in local storage
                    console.error(e);
                    localStorage.removeItem(key);
                }
            }
        }
        _loaded = true;
        for (var i=0; i < _pending.length; i++) {
            _pending[i]();
        }
    });
});
