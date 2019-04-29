(function() {
    angular.module("App")
    .controller("datasetBeaconController", ["$routeParams", "Beacon", "Dataset", "User",
                                function($routeParams, Beacon, Dataset, User) {
        var localThis = this;
        localThis.queryResponses = [];
        localThis.search = search;

        activate();

        function activate() {
            Beacon.getBeaconReferences($routeParams.dataset, $routeParams.version)
		.then(function(data) {
		    if (data) {
			localThis.references = data;
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
		    if (!response.data.datasetAlleleResponses[0]) {
			localThis.queryResponses.push({
                            "response": { "state": "Absent" },
                            "query": {
				"chromosome":      localThis.chromosome,
				"position":        localThis.position,
				"allele":          localThis.allele,
				"referenceAllele": localThis.referenceAllele,
				"reference":       localThis.reference
                            }
			});
		    }
		    else {
			localThis.queryResponses.push({
			    "response": { "state": "Present" },
			    "query": {
				"chromosome": response.data.datasetAlleleResponses[0].referenceName,
				"position": response.data.datasetAlleleResponses[0].start + 1, // Beacon is 0-based
				"allele": response.data.datasetAlleleResponses[0].alternateBases,
				"referenceAllele": response.data.datasetAlleleResponses[0].referenceBases,
				"reference": response.data.datasetAlleleResponses[0].datasetId.substring(0, 6),
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
                            "reference":       localThis.reference
                        }
                    });
                }
            );
        }
    }]);
})();
