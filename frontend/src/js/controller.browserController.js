(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "User", "Dataset", "Browser",
                             function( $routeParams,   User,   Dataset,   Browser) {
        var localThis = this;
        localThis.browserLink = browserLink;
        localThis.dataset = {'shortName':$routeParams.dataset};
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
    }]);
})();
