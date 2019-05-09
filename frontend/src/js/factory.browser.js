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

	function baseUrl(dataset, version) {
	    var url = "/api/dataset/" + dataset + "/";
	    if ( version ) {
		url += "version/" + version + "/"
	    }
	    url += 'browser/';
	    return url;
	}
	
        function getGene(dataset, version, gene) {
	    return $http.get(baseUrl(dataset, version) + "gene/" + gene).then(function(data) {
                return data.data;
            });
        }

        function getRegion(dataset, version, region) {
            return $http.get(baseUrl(dataset, version) + "region/" + region).then(function(data) {
                return data.data;
            });
        }

        function getTranscript(dataset, version, transcript) {
            return $http.get(baseUrl(dataset, version) + "transcript/" + transcript).then(function(data) {
                return data.data;
            });
        }

        function getVariant(dataset, version, variant) {
	    return $http.get(baseUrl(dataset, version) + "variant/" + variant).then(function(data) {
                return data.data;
	    });
        }

        function search(dataset, version, query) {
            return $http.get(baseUrl(dataset, version) + "search/" + query).then(function(data) {
                return data.data;
            });
        }

        function autocomplete(dataset, version, query) {
            return $http.get(baseUrl(dataset, version) + "autocomplete/" + query).then(function(data) {
                return data.data;
            });
        }

        function getVariants(dataset, version, datatype, item) {
            return $http.get(baseUrl(dataset, version) +  "variants/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }

        function getCoverage(dataset, version, datatype, item) {
            return $http.get(baseUrl(dataset, version) + "coverage/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }

        function getCoveragePos(dataset, version, datatype, item) {
            return $http.get(baseUrl(dataset, version) + "coverage_pos/" + datatype + "/" + item).then(function(data) {
                return data.data;
            });
        }
    }]);
})();
