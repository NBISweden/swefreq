(function() {
    angular.module("App")
    .controller("datasetController", ["$http", "$routeParams", "User", "Dataset",
                                function($http, $routeParams, User, Dataset) {
        var localThis = this;
        var dataset = $routeParams["dataset"];

        User().then(function(data) {
            localThis.user = data.data;
        });

        Dataset($routeParams["dataset"], $routeParams["version"]).then(function(data){
                localThis.dataset = data.dataset;
                localThis.collections = data.collections;
                localThis.study = data.study;
            },
            function(error) {
                localThis.error = error;
            });
    }]);
})();
