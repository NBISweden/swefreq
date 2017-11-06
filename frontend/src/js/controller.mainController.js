(function() {
    angular.module("App")
    .controller("mainController", [ "$location", "User", function($location, User) {
        var localThis = this;
        localThis.url = function () { return $location.path(); };
        localThis.logged_in = false;

        User.getUser().then(function(data) {
            localThis.user = data;
            if ( localThis.user.user !== null ) {
                localThis.logged_in = true;
            }
        });
    }]);
})();
