(function() {
    angular.module("App")
    .controller("datasetDownloadController", ["$http", "$routeParams", "User", "Dataset", "DatasetUsers", "Log",
                                function($http, $routeParams, User, Dataset, DatasetUsers, Log) {
        var localThis = this;
        var dataset = $routeParams.dataset;
        localThis.authorization_level = "loggedout";
        localThis.sendRequest = sendRequest;
        localThis.consented = consented;

        activate();


        function activate() {
            $http.get("/api/countries").then(function(data) {
                localThis.availableCountries = data.data.countries;
            });

            User.getUser().then(function(data) {
                localThis.user = data;
                updateAuthorizationLevel();
            });

            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                    updateAuthorizationLevel();
                },
                function(error) {
                    localThis.error = error;
                }
            );

            var file_uri = "/api/datasets/" + dataset + "/files";
            if ( $routeParams.version ) {
                file_uri = "/api/datasets/" + dataset + "/versions/" + $routeParams.version + "/files";
            }
            $http.get(file_uri).then(function(data) {
                localThis.files = data.data.files;
            });
        }

        function updateAuthorizationLevel() {
            if (!localThis.hasOwnProperty("user") || localThis.user.user == null) {
                localThis.authorization_level = "loggedout";
            }
            else if (localThis.hasOwnProperty("dataset")) {
                localThis.authorization_level = localThis.dataset.authorization_level;
            }
        }

        function sendRequest(valid) {
            if (!valid) {
                return;
            }
            DatasetUsers.requestAccess(dataset, localThis.user)
                .then(function(data) {
                    localThis.authorization_level = "thank-you";
                }
            );
        };

        var has_already_logged = false;
        function consented() {
            if (!has_already_logged){
                has_already_logged = true;
                Log.consent(dataset, localThis.dataset.version.version);
            }
        };
    }]);
})();
