(function() {
    angular.module('App')
    .factory('DatasetVersions', function($http, $q) {
        return function(dataset) {
            // Hide the ugly implementation details by using $q to return an
            // async object that resolves to the content of the REST call.
            return $q(function(resolve,reject) {
                $http.get('/api/datasets/' + dataset + '/versions')
                    .then(function(data) {
                        resolve(data.data.data);
                    })
            });
        };
    });
})();
