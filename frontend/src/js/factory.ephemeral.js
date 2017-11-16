(function() {
    angular.module("App")
    .factory("EphemeralLink", ["$http", "$cookies", function($http, $cookies) {
        return {
            getEphemeral: getEphemeral
        };

        function getEphemeral(dataset, version) {
            url = "/api/datasets/" + dataset;
            if (version) {
                url += "/versions/" + version;
            }
            url += "/ephemeral_link"
            return $http.post(
                    url,
                    $.param({"_xsrf": $cookies.get("_xsrf")})
                );
        }
    }]);
})();
