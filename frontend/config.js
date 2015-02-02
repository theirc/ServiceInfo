var config_data = {
    api_location: "//localhost:8000/",
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
            console.log(key, value);
            localStorage[key] = value;
        }
    },
    remove: function(key) {
        localStorage.removeItem(key);
    },

    load: function(type, cb) {
        if (!_loaded) {
            _pending.push(function() {
                config.load(type, cb);
            })
            return;
        }
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
    },
}

var $ = require('jquery');
$(function($){
    var config_url = './config.json';
    $.getJSON(config_url, function(data) {
        $.extend(config_data, data);
        for (var key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                config_data[key] = localStorage[key];
            }
        }
        _loaded = true;
        for (var i=0; i < _pending.length; i++) {
            _pending[i]();
        }
    });
});
