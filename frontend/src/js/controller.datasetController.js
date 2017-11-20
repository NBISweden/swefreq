(function() {
    angular.module("App")
    .controller("datasetController", ["$routeParams", "User", "Dataset",
                                function($routeParams, User, Dataset) {
        var localThis = this;

        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
            });

            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                    localThis.collections = data.collections;
                    localThis.study = data.study;
                },
                function(error) {
                    localThis.error = error;
                }
            );
        }
    }]);
})();
