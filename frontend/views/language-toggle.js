var Backbone = require('backbone'),
config = require("../config"),
api = require("../api"),
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
        if (!config.isset('forever.language')) {
            this.show(true);
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
                    $.ajax(api.getAPIPrefix() + 'api/language/', {
                        type: 'POST',
                        headers: headers,
                        dataType: 'html',
                        data: {
                            'language': value
                        },
                        error: function (data) {
                            console.error('E', data);
                        },
                    });
                }
            }
        });
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({

        }));
         /* We have to be firm with i18next to stop it trying to load all sorts
           of non-existent language files like 'en-US' and 'dev' */
        i18n.init(
            {
                fallbackLng: ['en', 'ar', 'fr'],
                fallbackOnEmpty: true,
                lngWhitelist: ['en', 'ar', 'fr'],
                preload: ['en', 'ar', 'fr'],
                useCookie: false
            },
            function () {}
        );
    },

    setLanguage: function(lang) {
        i18n.init({
            lng: lang
        }, function(t){
            $("body").i18n();
        });
        if (lang === 'ar') {
            /* RIGHT to LEFT */
            $('body').attr('dir', 'rtl');
            $('body').removeClass('left-to-right');
            $('body').addClass('right-to-left');
            $('link.load-style').attr('href', "styles/site-rtl.css");
        } else {
            $('body').attr('dir', 'ltr');
            $('body').removeClass('right-to-left');
            $('body').addClass('left-to-right');
            $('link.load-style').attr('href', "styles/site-ltr.css");
        }
    },

    hide: function(immediate) {
        var target;
        if (window.innerHeight > window.innerWidth){
            target = $('#menu-toggle').position();
        } else {
            target = $('#menu-container').find('.menu-item-language').position();
        }
        var anim = {
            top: target.top - $('.language-toggle').height()/2,
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

    show: function(immediate) {
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
        if (immediate) {
            $el.addClass('no-animate');
            $el.css({
                top: '0px',
                left: 'auto',
            })
        } else {
            $el.animate(anim, {duration: 0.5, complete: function() {
                $el.css({
                    top: '0px',
                    left: 'auto',
                })
            }});
        }
        $el.removeClass('hidden');
        setTimeout(function() {
            $el.removeClass('no-animate');
        }, 0);
    },

    events: {
        "click button": function(ev) {
            var lang = $(ev.target).data('lang');
            config.set('forever.language', lang);
            this.hide();
        },
    },
})
