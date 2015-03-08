var hashtrack = require('hashtrack');
var service = require('./models/service');
var servicetype = require('./models/servicetype');


var query = "";
hashtrack.onhashvarchange('q', function(_, value) {
    query = value;
    $('#page').trigger('search', value)
})
hashtrack.onhashvarchange('t', function(_, value) {
    query = value;
    $('#page').trigger('search', value)
})

module.exports = {
    services: new service.PublicServices(),
    servicetypes: new servicetype.ServiceTypes(),

    populateServiceTypeDropdown: function() {
        var servicetypes = this.servicetypes;
        var $select = $('select.query-service-type');

        servicetypes.fetch().then(function() {
            $.each(servicetypes.models, function() {
                var d = this.data();
                $select.append('<option value="'+d.number +'">'+d.name+'</option>')
            })
            var t = hashtrack.getVar('t');
            if (t) {
                $select.val(t);
            }
        });
    },

    refetchServices: function() {
        var query = hashtrack.getVar('q');
        var type = hashtrack.getVar('t');
        var params = {
            search: query,
            type_numbers: type,
        };

        return this.services.fetch({data: params});
    },
};
