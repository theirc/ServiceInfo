var config = {
    api_location: "//localhost:8000",
    lang: 'en',
};

module.exports = {
    get: function(k) { return config[k]; },
    set: function(k, v) {
        config[k] = v;
        if (k.indexOf('forever.') === 0) {
            console.log(k, v);
            localStorage[k] = v;
        }
    },
    remove: function(k) {
        localStorage.removeItem(k);
    },

    load: function(t) {
        $.ajax('//localhost:4005/api/'+t+'/', {
            method: 'GET',
            success: function(data) {
                console.log(data);
            },
            error: function(e) {
                console.error(e);
            },
        });
    },
}

var $ = require('jquery');
$(function($){
    var config_url = document.location.pathname + 'config.json';
    $.getJSON(config_url, function(data) {
        $.extend(config, data);
        for (var k in localStorage) {
            if (localStorage.hasOwnProperty(k)) {
                config[k] = localStorage[k];
            }
        }
    });
});
