(function() {
    angular.module("App")
    .factory("Schema", ["$http", function($http) {
        return {
            getSchema: getSchema,
        };

        function getSchema(dataset, version) {
            // Check if we have a dataset
            if ( dataset ) {
                var schemaUri = "/api/datasets/" + dataset + "/schema";

                // check if a specific version is requested
                if ( version ) {
                    schemaUri = "/api/datasets/" + dataset + "/versions/" + version + "/schema";
                }

                // Add the dataset information to the static data, and return it.
                return $http.get(schemaUri).then( function(schema) {
                    return $http.get("/static/json/bioschema.json")
                                .then( function(data) {
                                    data.data.dataset = schema.data;
                                    return data.data;
                        });
                    });
            }

            // Else return the static information
            return $http.get("/static/json/bioschema.json")
                 .then( function(data) {
                     return data.data;
                 });
        }
    }]);
})();
