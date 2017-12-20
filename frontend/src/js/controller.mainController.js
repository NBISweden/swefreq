(function() {
    angular.module("App")
    .controller("mainController", ["$location", "User", function($location, User) {
        var localThis = this;
        localThis.url = function() { return $location.path(); };
        localThis.loggedIn = false;

        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
                if ( localThis.user.user !== null ) {
                    localThis.loggedIn = true;
                }
            });
        }
    }]);
})();
