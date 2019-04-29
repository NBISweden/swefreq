(function() {
    angular.module("App")
    .factory("Beacon", ["$http", function($http) {
        return {
            getBeaconReferences: getBeaconReferences,
            queryBeacon: queryBeacon
        };

        function getBeaconReferences(name, version) {
            return $http.get("/api/beacon-elixir/").then(function(data) {
                var d = data.data.datasets;

		if (version) {
                    for (var i = 0; i < d.length; i++) {
			var dataset = d[i].id;
			if (dataset.indexOf(name) != -1 && dataset.indexOf(version) != -1) {
			    return [dataset.split(":")[0].substring(0, 6)];
			}
                    }
		}
		else {
		    var references = [];
		    for (var i = 0; i < d.length; i++) {
			var dataset = d[i].id;
			if (dataset.indexOf(name) != -1) {
			    references.push(dataset);
			}
                    }
		    var highest_ver = 0;
		    var reference = "";
		    for (var i = 0; i < references.length; i++) {
			var ver = parseInt(dataset.split(":")[2]);
			if (ver > highest_ver) {
			    highest_ver = ver;
			    reference = dataset.split(":")[0].substring(0, 6);
			}
		    }
		    return [reference]
		}
            });
        }

        function queryBeacon(query) {
            return $http.get("/api/beacon-elixir/query", {
                    "params": {
                        "referenceName":   query.chromosome,
                        "start":           query.position - 1, // Beacon is 0-based
                        "alternateBases":  query.allele,
                        "referenceBases":  query.referenceAllele,
                        "datasetIds":      query.dataset.shortName,
                        "assemblyId":      query.reference,
			"includeDatasetResponses": "HIT"
                    }
                }
            );
        }
    }]);
})();
