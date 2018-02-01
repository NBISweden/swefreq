(function() {
    angular.module("App")
    .factory("SFTPAccess", ["$http", "$cookies", function($http, $cookies) {
        return {
            getCredentials: getCredentials,
            createCredentials: createCredentials,
        };

        function getCredentials( dataset ) {
            return $http.get("/api/datasets/" + dataset + "/sftp_access")
                .then(function(data) {
                    return data.data;
                });
        }

        function createCredentials( dataset ) {
            $.ajax({
              url:"/api/datasets/" + dataset + "/sftp_access",
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
