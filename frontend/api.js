"use strict";

var config = require('./config');

module.exports = {
    request: function(method, path, data) {
        return new Promise(function(resolve, error) {
            var headers = {};
            var token = config.get('forever.authToken');
            if (token) {
                headers['ServiceInfoAuthorization'] = 'Token ' + token;
            }
            $.ajax(config.get('api_location')+path, {
                processData: false,
                data: JSON.stringify(data),
                type: method,
                contentType: 'application/json',
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
