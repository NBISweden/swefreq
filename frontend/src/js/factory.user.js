(function() {
    angular.module("App")
    .factory("User", ["$http", function($http) {
        return {
            getUser: getUser,
            getDatasets: getDatasets,
        };

        function getUser() {
            return $http.get("/api/users/me")
                .then(function(data) {
                    return data.data;
                }
            );
        }

        function getDatasets() {
            return $http.get("/api/users/datasets")
                .then(function(data) {
                    return data.data.data;
                }
            );
        }
    }]);
})();
