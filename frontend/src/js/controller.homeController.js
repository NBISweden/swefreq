(function() {
    angular.module("App")
    .controller("homeController", ["DatasetList", function(DatasetList) {
        var localThis = this;
        localThis.datasets = [];
        DatasetList.getDatasetList().then(function(datasets) {
            localThis.datasets = datasets;
        });
    }]);
})();
