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

    events: {
        "click button": function(ev) {
            var lang = $(ev.target).data('lang');
            localStorage['lang'] = lang;
            this.setLanguage(lang);
        },
    },
})
