(function() {
    angular.module("App")
    .controller("mainController", ["$location", "$cookies", "$scope", "User",
                          function( $location,   $cookies,   $scope,   User) {
        var localThis = this;
        localThis.url = function() { return $location.path(); };
        localThis.loggedIn = false;
        localThis.loginType = "none";
        localThis.msg = {"level":"", "msg":""};
        activate();

        function activate() {
            // This function is the same as is run from schema-injector.js.
            // It re-runs every time the route changes to keep the schema.org
            // annotation updated.
            // It passes the new url to the backend to update the the schema tag
            // based on what is currently being browsed.
            $scope.$on("$routeChangeStart", function() {
                $.getJSON( "/api/schema?url=" + $location.path(), function(data) {
                  $("#ldJsonTarget").html( JSON.stringify(data, null, 2) );
                });
            });
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

    }]);
})();
