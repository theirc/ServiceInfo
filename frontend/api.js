"use strict";

var config = require('./config');

module.exports = {
    getAPIPrefix: function() {
        var api_prefix = "//" + config.get('api_host') + ':' + config.get('api_port') + "/";
        return api_prefix;
    },
    request: function(method, path, data) {
        var api = this;
        return new Promise(function(resolve, error) {
            var headers = {};
            var token = config.get('forever.authToken');

            if (token) {
                headers['ServiceInfoAuthorization'] = 'Token ' + token;
            }
            $.ajax(api.getAPIPrefix() + path, {
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
