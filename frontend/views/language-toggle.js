var Backbone = require('backbone'),
template = require("../templates/language-toggle.hbs"),
i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
        this.setLanguage(localStorage['lang'] || 'en');
        if (localStorage['lang']) {
            this.hide(true);
        }
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({

        }));
        i18n.init(function(t){

        })
    },

    setLanguage: function(lang) {
        i18n.init(function(t){
            $("body").i18n({
                lng: lang,
            });
        });
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
            localStorage['lang'] = lang;
            this.setLanguage(lang);
            this.hide();
        },
    },
})
