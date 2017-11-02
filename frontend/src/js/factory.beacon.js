(function() {
    angular.module("App")
    .factory("Beacon", function($http, $q) {
        var service = {};

        function _getBeaconReferences(name) {
            var references = [];
            for (var i = 0; i<service.data["datasets"].length; i++) {
                var dataset = service.data["datasets"][i];
                if ( dataset["id"] == name ) {
                    references.push(dataset["reference"]);
                }
            }
            return references;
        }

        service.getBeaconReferences = function(name) {
            var defer = $q.defer();
            if ( service.hasOwnProperty("id") ) {
                defer.resolve( _getBeaconReferences(name) );
            }
            else {
                $http.get("/api/beacon/info").success(function(data) {
                    service.data = data;
                    defer.resolve(_getBeaconReferences(name));
                });
            }
            return defer.promise;
        };

        service.queryBeacon = function(query) {
            return $http.get("/api/beacon/query", {
                    "params": {
                        "chrom":           query.chromosome,
                        "pos":             query.position - 1, // Beacon is 0-based
                        "allele":          query.allele,
                        "referenceAllele": query.referenceAllele,
                        "dataset":         query.dataset.short_name,
                        "ref":             query.reference
                    }
                });
        };

        return service;
    });
})();
