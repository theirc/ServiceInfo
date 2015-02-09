var config_data = {
    //api_location: "//localhost:8000/",
    lang: 'en',
};
var _loaded = false;
var _pending = [];

var config = module.exports = {
    get: function(key) {
        return config_data[key];
    },
    set: function(key, value) {
        config_data[key] = value;
        if (key.indexOf('forever.') === 0) {
            localStorage[key] = value;
        }
        this._triggerChange(key, 'set', value);
    },
    remove: function(key) {
        localStorage.removeItem(key);
        this._triggerChange(key, 'remove');
    },

    change: function(key, cb) {
        if (typeof this._changeHandlers[key] === 'undefined') {
            this._changeHandlers[key] = [];
        }
        this._changeHandlers[key].push(cb);
    },
    _changeHandlers: {},
    _triggerChange: function(key) {

        if (key in this._changeHandlers) {
            for (var i=0; i < this._changeHandlers[key].length; i++) {
                this._changeHandlers[key][i].apply(this, arguments)
            }
        }
    },

    load: function(type, cb) {
        this.ready(function(){
            $.ajax(config.get('api_location')+'api/'+type+'/', {
                method: 'GET',
                success: function(data) {
                    config_data[type] = data.results;
                    cb(null, data.results);
                },
                error: function(e) {
                    cb(e);
                },
            });
        })
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

var $ = require('jquery');
$(function($){
    var config_url = './config.json';
    $.getJSON(config_url, function(data) {
        $.extend(config_data, data);
        for (var key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                config.set(key, localStorage[key]);
            }
        }
        _loaded = true;
        for (var i=0; i < _pending.length; i++) {
            _pending[i]();
        }
    });
});
