(function() {
    angular.module("App")
    .controller("datasetDownloadController", ["$location", "$http", "$routeParams", "clipboard", "User", "Dataset", "DatasetUsers", "Log", "DatasetFiles", "TemporaryLink",
                                function($location, $http, $routeParams, clipboard, User, Dataset, DatasetUsers, Log, DatasetFiles, TemporaryLink) {
        var localThis                 = this;
        var dataset                   = $routeParams.dataset;
        localThis.authorization_level = "loggedout";
        localThis.sendRequest         = sendRequest;
        localThis.consented           = consented;
        localThis.createTemporaryLink = createTemporaryLink;
        localThis.copyLink            = copyLink;
        localThis.canCopy             = clipboard.supported;

        localThis.host = $location.protocol() + "://" + $location.host();

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

            DatasetFiles.getFiles($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.files = data;
                }
            );
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

        function createTemporaryLink() {
            TemporaryLink.getTemporary($routeParams.dataset, $routeParams.version).success(function(data) {
                localThis.temporaries = true;
                for (let file of localThis.files) {
                    file["temp_url"] = localThis.host
                                     + file["dirname"] + "/"
                                     + data.hash + "/"
                                     + file["name"];
                    file["expires_on"] = data.expires_on;
                }
            });
        };

        function copyLink(link) {
            clipboard.copyText(link);
        }
    }]);
})();
