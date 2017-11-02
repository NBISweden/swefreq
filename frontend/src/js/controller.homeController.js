(function() {
    angular.module("App")
    .controller("homeController", ["$http", "$sce", "DatasetList", function($http, $sce, DatasetList) {
        var localThis = this;
        localThis.datasets = [];
        DatasetList().then(function(datasets) {
            localThis.datasets = datasets;
        });
    }]);
})();
