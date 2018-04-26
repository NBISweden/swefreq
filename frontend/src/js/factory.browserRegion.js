(function() {
    angular.module("App")
    .factory("browserRegion", ["$http", function($http) {
        return {
            getRegion: getRegion,
        };

        function getRegion(dataset, region) {
            return $http.get("/api/datasets/" + dataset + "/browser/region/" + region).then(function(data) {
                return data.data;
            });
        }
    }]);
})();
