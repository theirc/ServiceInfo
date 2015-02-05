"use strict";

var config = require('./config');

module.exports = {
    request: function(method, path) {
        return new Promise(function(resolve, error) {
            var headers = {};
            var token = config.get('forever.authToken');
            if (token) {
                headers['ServiceInfoAuthorization'] = 'Token ' + token;
            }
            $.ajax(config.get('api_location')+path, {
                type: method,
                contentType: 'JSON',
                headers: headers,
                success: function(resp) {
                    resolve(resp)
                },
                error: function(e) {
                    error(e);
                },
            });
        });
    }
};
