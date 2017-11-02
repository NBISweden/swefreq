(function() {
    angular.module('App')
    .factory('Log', function($http, $cookies) {
        var service = {};
        $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";

        service.consent = function(dataset, version) {
            return $http.post('/api/datasets/' + dataset + '/log/consent/' + version,
                    $.param({'_xsrf': $cookies.get('_xsrf')})
                );
        };

        return service;
    });
})();
