(function() {
    angular.module("App")
    .factory("Dataset", ["$http", "$q", "$sce", function($http, $q, $sce) {
        return {
            getDataset: getDataset
        };

        function getDataset(dataset, version) {
            var state = {dataset: null};
            var defer = $q.defer();

            if (dataset === undefined) {
                return defer.reject("No dataset provided");
            }
            var dataset_uri = "/api/datasets/" + dataset;
            if (version) {
                dataset_uri += "/versions/" + version;
            }

            $q.all([
                $http.get(dataset_uri).then(function(data){
                    var d = data.data;
                    d.version.description = $sce.trustAsHtml( d.version.description );
                    d.version.terms       = $sce.trustAsHtml( d.version.terms );
                    state.dataset = d;
                }),
                $http.get("/api/datasets/" + dataset + "/collection").then(function(data){
                    state.collections = data.data.collections;
                    state.study = data.data.study;

                    var contact_name = state.study.contact_name;
                    state.study.contact_name_uc = contact_name.charAt(0).toUpperCase() + contact_name.slice(1);
                })
            ]).then(function(data) {
                    defer.resolve(state);
                },
                function(error) {
                    var error_message = "Can't find dataset " + dataset;
                    if (version) {
                        error_message += " version " + version;
                    }
                    defer.reject(error_message);
                }
            );

            return defer.promise;
        }
    }]);
})();
