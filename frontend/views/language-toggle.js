var Backbone = require('backbone'),
config = require("../config"),
template = require("../templates/language-toggle.hbs"),
i18n = require('i18next-client');

// To change the app's language, call config.set('forever.language', lang)
// where lang is e.g. 'en', 'fr', or 'ar'.
// The config change handler below will handle the magic.

module.exports = Backbone.View.extend({
    initialize: function(){
        var language = config.get('forever.language'),
            lt = this;
        this.render();
        this.setLanguage(language);
        if (config.isset('forever.language')) {
            this.hide(true);
        };
        // Get called when forever.language is changed in the config.
        // This will (1) update the app and (2) if the user is logged in,
        // update their preferred language.
        config.change('forever.language', function (key, change, value) {
            // If user is logged in, save their language preference
            var token,
                headers = {};
            if (change === 'set') {
                // Update the app
                lt.setLanguage(value);
                if (value) {
                    // make sure language toggle is hidden
                    lt.hide(true);
                }
                token = config.get('forever.authToken');
                if (token) {
                    // user is logged in
                    // remember user's preference in the backend
                    headers.ServiceInfoAuthorization = 'Token ' + token;
                    $.ajax(config.get('api_location') + 'api/language/', {
                        type: 'POST',
                        headers: headers,
                        data: {
                            'language': value
                        },
                        error: function (data) {
                            console.error(data);
                        }
                    });
                }
            }
        });
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({

        }));
        i18n.init(function(t){

        })
    },

    setLanguage: function(lang) {
        i18n.init({
              lng: lang
            }, function(t){
                $("body").i18n();
            }
        );
    },

    hide: function(immediate) {
        var target;
        if (window.innerHeight > window.innerWidth){
            target = $('#menu-toggle').position();
        } else {
            target = $('#menu-container').find('.menu-item-language').position();
        }
        var anim = {
            top: target.top,
            left: target.left,
        };
        this.$el.css(this.$el.position());
        this.$el.addClass('hidden');
        if (immediate) {
            this.$el.css(anim);
        } else {
            this.$el.animate(anim, {duration: 0.5});
        }

        this._hiddenPos = anim;
    },

    show: function() {
        var curPos = this.$el.position();
        var $el = this.$el;

        $el.css('visibility', 'hidden');
        $el.removeClass('hidden');
        $el.css({
            top: 'auto',
            left: 'auto',
        })

        var anim = $el.position();

        $el.addClass('hidden');
        $el.css(curPos);
        $el.css('visibility', 'visible');
        $el.animate(anim, {duration: 0.5, complete: function() {
            $el.css({
                top: 'auto',
                left: 'auto',
            })
        }});
        $el.removeClass('hidden');
    },

    events: {
        "click button": function(ev) {
            var lang = $(ev.target).data('lang');
            config.set('forever.language', lang);
            this.hide();
        },
    },
})
