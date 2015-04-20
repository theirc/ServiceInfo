var _initialized = false,
    _callbacks = [];

module.exports = {
    ready: function(callback) {
        // Call the callback after i18n has been initialized (or
        // immediately if it already has).
        if (_initialized) {
            callback();
        } else {
            _callbacks.push(callback);
        }

    },
    set_initialized: function() {
        // Whoever initializes i18n should call this afterward.
        _initialized = true;
        for (var i = 0; i < _callbacks.length; i++) {
            _callbacks[i]();
        }
    }
};
