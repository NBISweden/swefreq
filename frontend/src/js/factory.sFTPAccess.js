(function() {
    angular.module("App")
    .factory("SFTPAccess", ["$http", "$cookies", function($http, $cookies) {
        return {
            getCredentials: getCredentials,
            createCredentials: createCredentials,
        };

        function getCredentials() {
            return $http.get("/api/users/sftp_access")
                .then(function(data) {
                    return data.data;
                });
        }

        function createCredentials() {
            return $http.post("/api/users/sftp_access",
                              $.param({"_xsrf": $cookies.get("_xsrf")}),
                              {headers : {
                                "Content-Type": "application/x-www-form-urlencoded;"
                              }})
                .then( function(data) {
                    return data.data;
                });
        }
    }]);
})();
