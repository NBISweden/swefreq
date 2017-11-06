(function() {
    angular.module("App")
    .factory("User", function($http) {
        return {
            getUser: getUser,
        };

        function getUser() {
            return $http.get("/api/users/me")
                .then(function(data) {
                    return data.data
                }
            );
        };
    });
})();
