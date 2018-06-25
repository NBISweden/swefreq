(function() {
    angular.module("App")
    .factory("Browser", ["$http", function($http) {
        return {
            getGene:       getGene,
            getRegion:     getRegion,
            getTranscript: getTranscript,
            getVariant:    getVariant,
            search:        search,
            autocomplete:  autocomplete,
            getVariants:   getVariants,
            getCoverage:   getCoverage,
            getCoveragePos:getCoveragePos,
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

        function search(dataset, query) {
            return $http.get("/api/datasets/" + dataset + "/browser/search/" + query).then(function(data) {
                return data.data;
            });
        }

        function autocomplete(dataset, query) {
            return $http.get("/api/datasets/" + dataset + "/browser/autocomplete/" + query).then(function(data) {
                return data.data;
            });
        }

        function getVariants(dataset, datatype, item) {
            return $http.get("api/datasets/" + dataset + "/browser/variants/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }

        function getCoverage(dataset, datatype, item) {
            return $http.get("api/datasets/" + dataset + "/browser/coverage/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }

        function getCoveragePos(dataset, datatype, item) {
            return $http.get("api/datasets/" + dataset + "/browser/coverage_pos/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }
    }]);
})();
