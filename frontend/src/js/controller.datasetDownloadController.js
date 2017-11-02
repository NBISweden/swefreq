(function() {
    angular.module("App")
    .controller("datasetDownloadController", ["$http", "$routeParams", "User", "Dataset", "DatasetUsers", "Log",
                                function($http, $routeParams, User, Dataset, DatasetUsers, Log) {
        var localThis = this;
        var dataset = $routeParams["dataset"];
        localThis.authorization_level = "loggedout";

        $http.get("/api/countries").success(function(data) {
            localThis.availableCountries = data["countries"];
        });

        User().then(function(data) {
            localThis.user = data.data;
            updateAuthorizationLevel();
        });

        Dataset($routeParams["dataset"], $routeParams["version"]).then(function(data){
                localThis.dataset = data.dataset;
                updateAuthorizationLevel();
            },
            function(error) {
                localThis.error = error;
            });

        var file_uri = "/api/datasets/" + dataset + "/files";
        if ( $routeParams["version"] ) {
            file_uri = "/api/datasets/" + dataset + "/versions/" + $routeParams["version"] + "/files";
        }
        $http.get(file_uri).success(function(data){
            localThis.files = data.files;
        });

        function updateAuthorizationLevel () {
            if (!localThis.hasOwnProperty("user") || localThis.user.user == null) {
                localThis.authorization_level = "loggedout";
            }
            else if (localThis.hasOwnProperty("dataset")) {
                localThis.authorization_level = localThis.dataset.authorization_level;
            }
        };

        localThis.sendRequest = function(valid){
            if (!valid) {
                return;
            }
            DatasetUsers.requestAccess(
                    dataset, localThis.user
                ).success(function(data){
                    localThis.authorization_level = "thank-you";
                });
        };

        has_already_logged = false;
        localThis.consented = function(){
            if (!has_already_logged){
                has_already_logged = true;
                Log.consent(dataset, localThis.dataset.version.version);
            }
        };
    }]);
})();
