(function() {
    angular.module("App")
    .controller("navbarController", ["$routeParams", "Dataset", "DatasetVersions", function($routeParams, Dataset, DatasetVersions) {
        var localThis = this;
        localThis.is_admin = false;
        localThis.createUrl = createUrl;

        activate();

        function activate() {
            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.is_admin    = data.dataset.is_admin;
                    localThis.dataset     = data.dataset.short_name;
                    localThis.browser_uri = data.dataset.browser_uri;
                    localThis.urlBase     = "/dataset/" + localThis.dataset;
                    localThis.thisVersion = data.dataset.version.version;
                    if ($routeParams.version) {
                        localThis.urlBase += "/version/" + $routeParams.version;
                    }

                    DatasetVersions.getDatasetVersions(localThis.dataset)
                        .then(function(data) {
                            for (var i = 0; i < data.length; i++) {
                                if ( data[i].name === localThis.thisVersion ) {
                                    data[i].active = true;
                                    break;
                                }
                            }
                            localThis.versions = data;
                        }
                    );
                }
            );
        }

        function createUrl(subpage, version) {
            if (subpage === "admin") {
                return "/dataset/" + localThis.dataset + "/" + subpage;
            }
            if (subpage === "main") {
                subpage = "";
            }
            if (version) {
                return "/dataset/" + localThis.dataset + "/version/" + version + "/" + subpage;
            }
            return localThis.urlBase + "/" + subpage;
        }
    }]);
})();
