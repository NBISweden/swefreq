(function() {
    angular.module("App")
    .controller("datasetBeaconController", ["$routeParams", "Beacon", "Dataset", "User",
                                function($routeParams, Beacon, Dataset, User) {
        var localThis = this;
        localThis.queryResponses = [];
        localThis.search = search;
        localThis.fillExample = fillExample;

        activate();

        function activate() {
            Beacon.getBeaconReferences($routeParams.dataset, $routeParams.version)
		.then(function(data) {
		    if (data) {
			localThis.beaconInfo = data;
		    }
                });

            User.getUser().then(function(data) {
                localThis.user = data;
            });

            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                },
                function(error) {
                    localThis.error = error;
                }
            );
        }

        function search() {
            Beacon.queryBeacon(localThis)
                .then(function(response) {
		    if (response.data.exists===false) { // value may be null -> error
			localThis.queryResponses.push({
                            "response": { "state": "Absent" },
                            "query": {
				"chromosome":      localThis.chromosome,
				"position":        localThis.position,
				"allele":          localThis.allele,
				"referenceAllele": localThis.referenceAllele,
                            }
			});
		    }
		    else if (response.data.exists===true) {
			localThis.queryResponses.push({
			    "response": { "state": "Present" },
			    "query": {
				"chromosome":      localThis.chromosome,
				"position":        localThis.position,
				"allele":          localThis.allele,
				"referenceAllele": localThis.referenceAllele,
                            }
			});
		    }
		    else {
			localThis.queryResponses.push({
                            "response": { "state": "Error" },
                            "query": {
				"chromosome":      localThis.chromosome,
				"position":        localThis.position,
				"allele":          localThis.allele,
				"referenceAllele": localThis.referenceAllele,
                            }
			});
                    }
		},
                function() {
                    localThis.queryResponses.push({
                        "response": { "state": "Error" },
                        "query": {
                            "chromosome":      localThis.chromosome,
                            "position":        localThis.position,
                            "allele":          localThis.allele,
                            "referenceAllele": localThis.referenceAllele,
                        }
                    });
                }
            );
        }
	function fillExample() {
	    localThis.chromosome = "22";
	    localThis.position = 46615880;
	    localThis.referenceAllele = "T";
	    localThis.allele = "C";
	}
    }]);
})();
