(function() {
    angular.module("App")
    .controller("datasetAdminController", ["$routeParams", "User", "Dataset", "DatasetUsers",
                                function($routeParams, User, Dataset, DatasetUsers) {
        var localThis = this;
        var dataset = $routeParams["dataset"];

        getUsers();
        function getUsers() {
            DatasetUsers.getUsers( dataset ).then( function(data) {
                localThis.users = data;
            });
        }

        User.getUser().then(function(data) {
            localThis.user = data;
        });

        Dataset.getDataset($routeParams["dataset"], $routeParams["version"]).then(function(data){
                localThis.dataset = data.dataset;
            },
            function(error) {
                localThis.error = error;
            });

        localThis.revokeUser = function(userData) {
            DatasetUsers.revokeUser(
                    dataset, userData.email
                ).success(function(data){
                    getUsers();
                });
        };

        localThis.approveUser = function(userData){
            DatasetUsers.approveUser(
                    dataset, userData.email
                ).success(function(data) {
                    getUsers();
                });
        };
    }]);
})();
