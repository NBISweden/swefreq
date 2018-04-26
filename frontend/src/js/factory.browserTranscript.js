(function() {
    angular.module("App")
    .factory("browserTranscript", ["$http", function($http) {
        return {
            getTranscript: getTranscript,
        };

        function getTranscript(dataset, transcript) {
            return $http.get("/api/datasets/" + dataset + "/browser/transcript/" + transcript).then(function(data) {
                return data.data;
            });
        }
    }]);
})();
