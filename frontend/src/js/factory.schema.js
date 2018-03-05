(function() {
    angular.module("App")
    .factory("Schema", ["$http", function($http) {
        return {
            getSchema: getSchema,
        };

        function getSchema(dataset, version) {
            // Check if we have a dataset

            var datasetSchema = null;
            if ( dataset ) {
                var schemaUri = "/api/datasets/" + dataset + "/schema";

                // check if a specific version is requested
                if ( version ) {
                    schemaUri = "/api/datasets/" + dataset + "/versions/" + version + "/schema";
                }

                $http.get(schemaUri).then( function(data) {
                    datasetSchema = data.data;
                });
            }

            var schema = $http.get("/static/json/bioschema.json")
                 .then( function(data) {
                     if ( datasetSchema )
                         data.data.dataset = datasetSchema;
                     return data.data;
                 });

            return schema;
        }
    }]);
})();
