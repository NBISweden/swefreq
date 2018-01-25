(function() {
    angular.module("App")
    .controller("loginController", ["$http", "User", function($http, User) {
        var localThis = this;
        localThis.postTransferForm = postTransferForm;

        function postTransferForm(valid) {
            if (!valid) {
                return;
            }
            User.transferAccount().then(function(data) {
                    window.location.replace( data.data.redirect );
                });
        }

    }]);
})();



