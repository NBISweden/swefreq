(function() {
    angular.module("App")
    .controller("datasetAdminController", ["$routeParams", "$http", "$cookies", "User", "Dataset", "DatasetUsers",
                                function($routeParams, $http, $cookies, User, Dataset, DatasetUsers) {
        var localThis = this;
        localThis.revokeUser = revokeUser;
        localThis.approveUser = approveUser;
        localThis.postSFTPForm = postSFTPForm;
        localThis.sftp = {"user":"", "password":"", "expires":null};

        activate();

        function activate() {
            getUsers();

            User.getUser().then(function(data) {
                localThis.user = data.data;
            });

            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                },
                function(error) {
                    localThis.error = error;
                }
            );

            $http.get("/api/datasets/" + $routeParams.dataset + "/sftp_access")
                 .then(function(data) {
                     return localThis.sftp = data.data;
                 });

        }

        function getUsers() {
            DatasetUsers.getUsers( $routeParams.dataset )
                .then(function(data) {
                    localThis.users = data;
                }
            );
        }


        function revokeUser(userData) {
            DatasetUsers.revokeUser(
                    $routeParams.dataset, userData.email
                ).then(function() {
                    getUsers();
                }
            );
        }

        function approveUser(userData){
            DatasetUsers.approveUser(
                    $routeParams.dataset, userData.email
                ).then(function() {
                    getUsers();
                }
            );
        }

        function postSFTPForm(valid) {
            if (!valid) {
                return;
            }
            $.ajax({
              url:"/api/datasets/" + $routeParams.dataset + "/sftp_access",
              type:"POST",
              data:{"_xsrf": $cookies.get("_xsrf")},
              contentType:"application/x-www-form-urlencoded",
              success: function(data){
                  $("#sftp-user").html(data.user);
                  $("#sftp-password").html(data.password);
                  $("#sftp-expires").html(data.expires);
              }
            });
        }
    }]);
})();
