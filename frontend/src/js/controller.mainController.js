(function() {
    angular.module("App")
    .controller("mainController", ["$location", "$cookies", "$http", "User", function($location, $cookies, $http, User) {
        $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
        var localThis = this;
        localThis.url = function() { return $location.path(); };
        localThis.loggedIn = false;
        localThis.loginType = "none";
        localThis.msg = {"level":"", "msg":""};
        localThis.transferAccount = transferAccount;
        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
                localThis.loginType = data.loginType;
                if ( localThis.user.user !== null ) {
                    localThis.loggedIn = true;
                }
            });
            localThis.msg = $cookies.getObject("msg");
            $cookies.remove("msg");
        }

        function transferAccount(valid) {
            if (!valid) {
                return;
            }
            $http.post("/api/users/elixir_transfer",
                    $.param({"_xsrf": $cookies.get("_xsrf")})
                ).then(function(data) {
                    window.location.replace( data.data.redirect );
                });
        }
    }]);
})();
