var Backbone = require('backbone'),
template = require("../templates/language-toggle.hbs"),
i18n = require('i18next-client');

module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
        this.setLanguage(localStorage['lang'] || 'en');
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

    hide: function() {
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
        this.$el.addClass('hidden');
        this.$el.animate(anim, {duration: 0.5});
    },

    show: function() {
        this.$el.css('top', 'auto');
        this.$el.css('left', 'auto');
        this.$el.css.removeClass('hidden');
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
