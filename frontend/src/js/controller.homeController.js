(function() {
    angular.module("App")
    .controller("homeController", ["DatasetList", function(DatasetList) {
        var localThis = this;
        localThis.datasets = [];

        activate();

        function activate() {
            DatasetList.getDatasetList().then(function(datasets) {
                localThis.datasets = datasets;
            });
        }
    }]);
})();
