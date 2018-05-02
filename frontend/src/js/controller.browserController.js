(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "$scope", "User", "Dataset", "Browser",
                             function( $routeParams,   $scope,   User,   Dataset,   Browser) {
        var localThis = this;
        $scope.search = {"query":"", "autocomplete":[]};
        localThis.browserLink = browserLink;
        localThis.dataset = {'shortName':$routeParams.dataset};
        localThis.autocomplete = autocomplete;
        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
            });
            if ($routeParams.transcript) {
                Browser.getTranscript($routeParams.dataset, $routeParams.transcript).then( function(data) {
                    localThis.transcript = data.transcript;
                    localThis.gene       = data.gene;
                });
            }
            if ($routeParams.region) {
                Browser.getRegion($routeParams.dataset, $routeParams.region).then( function(data) {
                    localThis.region = data.region;
                });
            }
            if ($routeParams.gene) {
                Browser.getGene($routeParams.dataset, $routeParams.gene).then( function(data) {
                    localThis.gene = data.gene;
                    localThis.variants = data.variants;
                    localThis.transcripts = data.transcripts;
                });
            }
            if ($routeParams.variant) {
                Browser.getVariant($routeParams.dataset, $routeParams.variant).then( function(data) {
                    localThis.variant = data.variant;
                });
            }
            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                },
                function(error) {
                    localThis.error = error;
            });
        }

        function browserLink(link) {
            return "/dataset/" + $routeParams.dataset + "/browser/" + link;
        }

        function autocomplete() {
            if ($scope.search.query) {
                Browser.autocomplete($routeParams.dataset, $scope.search.query)
                       .then( function(data) {
                            $scope.search.autocomplete = data.values;
                        });
            } else {
                $scope.search.autocomplete = [];
            }
        }
    }]);
})();
