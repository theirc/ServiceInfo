var _config = {
    api_location: "//localhost:8000/",
    lang: 'en',
};
var _loaded = false;
var _pending = [];

var config = module.exports = {
    get: function(k) { return _config[k]; },
    set: function(k, v) {
        _config[k] = v;
        if (k.indexOf('forever.') === 0) {
            console.log(k, v);
            localStorage[k] = v;
        }
    },
    remove: function(k) {
        localStorage.removeItem(k);
    },

    load: function(t, cb) {
        if (!_loaded) {
            _pending.push(function() {
                config.load(t, cb);
            })
            return;
        }
        $.ajax(config.get('api_location')+'api/'+t+'/', {
            method: 'GET',
            success: function(data) {
                _config[t] = data.results;
                cb(null, data.results);
            },
            error: function(e) {
                cb(e);
            },
        });
    },
}

var $ = require('jquery');
$(function($){
    var config_url = './config.json';
    $.getJSON(config_url, function(data) {
        $.extend(_config, data);
        for (var k in localStorage) {
            if (localStorage.hasOwnProperty(k)) {
                _config[k] = localStorage[k];
            }
        }
        _loaded = true;
        for (var i=0; i < _pending.length; i++) {
            _pending[i]();
        }
    });
});
