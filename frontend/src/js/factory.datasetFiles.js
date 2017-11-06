(function() {
    angular.module("App")
    .factory("DatasetFiles", ["$http", function($http) {
        return {
            getFiles: getFiles,
        };

        function getFiles(dataset, version) {
            var file_uri = "/api/datasets/" + dataset + "/files";
            if ( version ) {
                file_uri = "/api/datasets/" + dataset + "/versions/" + version + "/files";
            }
            return $http.get(file_uri).then(function(data) {
                return data.data.files
            });
        }
    }]);
})();
