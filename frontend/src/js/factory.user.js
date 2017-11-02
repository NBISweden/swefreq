(function() {
    angular.module('App')
    .factory('User', function($http) {
        return function() {
            return $http.get('/api/users/me');
        };
    });
})();
