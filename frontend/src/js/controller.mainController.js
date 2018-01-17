(function() {
    angular.module("App")
    .controller("mainController", ["$location", "User", function($location, User) {
        var localThis = this;
        localThis.url = function() { return $location.path(); };
        localThis.loggedIn = false;
        localThis.loginType = "none";
        localThis.msg = {"level":"", "msg":""};
        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
                localThis.loginType = data.loginType;
                if ( localThis.user.user !== null ) {
                    localThis.loggedIn = true;
                }
            });
            User.getMessage().then(function(data) {
                localThis.msg = data;
            });
        }
    }]);
})();
