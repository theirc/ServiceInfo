var Backbone = require('backbone'),
    $ = require('jquery'),
    config = require('../config'),
    forms = require('../forms'),
    template = require("../templates/import-export.hbs"),
    i18n = require('i18next-client'),
    language = require('../language'),
    messages = require('../messages'),
    api = require('../api');


module.exports = Backbone.View.extend({
    initialize: function(){
        this.render();
    },

    render: function() {
        var $el = this.$el;
        this.$el.html(template({}));
        language.ready(function(){
            $el.i18n();
        });
    },

    events: {
        "click button#export": function(ev) {
            ev.preventDefault();

            // Get a signed URL for exports
            api.request('GET', 'api/export/').then(function(resp) {
                // point browser at the export URL we just fetched
                window.location = api.getAbsoluteAPIURL(resp.url);
            });
        },
        'submit': function(ev) {
            ev.preventDefault();
            messages.clear();
            var $form = $('form');
            var $submit = $form.find('.form-btn-submit');
            $submit.attr('disabled', 'disabled');

            $form.ajaxSubmit({
                contentType: 'multipart/form-data',
                url: api.getAbsoluteAPIURL('api/import/'),
                beforeSend: function(jqXHR) {
                    jqXHR.setRequestHeader('ServiceInfoAuthorization',
                            'Token ' + config.get('forever.authToken'));
                },
                error: function(xhr, statusText, statusText2, form) {
                    $submit.removeAttr('disabled');
                    if (xhr.status === 400) {
                        /* Error in the request */
                        var errors = xhr.responseJSON;
                        messages.add(i18n.t('Import-Tool.Errors'));
                        $.each(errors, function(k) {
                            for (var i = 0; i < this.length; i++) {
                                messages.add(this[i]);
                            }
                        });
                        return;
                    }
                    /* Something worse? */
                    messages.add(i18n.t("Global.FormSubmissionError"));
                    console.error(xhr);
                },
                success: function(/*response, statusText, xhr, form*/) {
                    $submit.removeAttr('disabled');
                    messages.add(i18n.t('Import-Tool.Success'));
                }
            });
        }
    }
});
