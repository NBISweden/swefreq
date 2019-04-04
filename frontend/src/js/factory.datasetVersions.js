(function() {
    angular.module("App")
    .factory("DatasetVersions", ["$http", function($http) {
        return {
            getDatasetVersions: getDatasetVersions,
        };
        function getDatasetVersions(dataset) {
            return $http.get("/api/dataset/" + dataset + "/versions")
                .then(function(data) {
                    return data.data.data;
                }
            );
        }
    }]);
})();
