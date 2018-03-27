(function() {
    angular.module("App")
    .controller("profileController", ["User", "Countries", "SFTPAccess", 
                              function(User,   Countries,   SFTPAccess) {
    var localThis = this;
    localThis.sftp = {"user":"", "password":"", "expires":null};
    localThis.createSFTPCredentials = function() {
        SFTPAccess.createCredentials()
            .then( function(data) {
                localThis.sftp = data;
            });
    };

    activate();

    function activate() {
        User.getUser().then(function(data) {
            localThis.user = data;
            setCountry();
        });

        Countries.getCountries().then(function(data) {
            localThis.availableCountries = data;
            setCountry();
        });

        User.getDatasets().then(function(data) {
            localThis.datasets = data;
        });

        SFTPAccess.getCredentials()
            .then( function(data) {
                localThis.sftp = data;
        });
    }

    function setCountry() {
        if (localThis.user && localThis.availableCountries) {
            var country = localThis.user.country;
            localThis.user.country = { name: country, id: country };
        }
    }
    }]);
})();
