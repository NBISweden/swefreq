(function() {
    angular.module("App")
    .factory("Browser", ["$http", function($http) {
        return {
            getGene:       getGene,
            getRegion:     getRegion,
            getTranscript: getTranscript,
            getVariant:    getVariant,
        };

        function getGene(dataset, gene) {
            return $http.get("/api/datasets/" + dataset + "/browser/gene/" + gene).then(function(data) {
                return data.data;
            });
        }

        function getRegion(dataset, region) {
            return $http.get("/api/datasets/" + dataset + "/browser/region/" + region).then(function(data) {
                return data.data;
            });
        }

        function getTranscript(dataset, transcript) {
            return $http.get("/api/datasets/" + dataset + "/browser/transcript/" + transcript).then(function(data) {
                return data.data;
            });
        }

        function getVariant(dataset, variant) {
            return $http.get("/api/datasets/" + dataset + "/browser/variant/" + variant).then(function(data) {
                return data.data;
            });
        }

    }]);
})();
