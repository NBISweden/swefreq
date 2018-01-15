(function() {
    angular.module("App")
    .controller("mainController", ["$location", "User", function($location, User) {
        var localThis = this;
        localThis.url = function() { return $location.path(); };
        localThis.loggedIn = false;
        localThis.loginType = 'none';
        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
                localThis.loginType = data.loginType
                if ( localThis.user.user !== null ) {
                    localThis.loggedIn = true;
                }
            });
        }
    }]);
})();
