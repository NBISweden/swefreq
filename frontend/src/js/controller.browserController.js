(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "$window", "User", "Dataset", "Browser",
                             function( $routeParams,   $window,   User,   Dataset,   Browser) {
        var localThis = this;
        localThis.query = "";
        localThis.suggestions = "";
        localThis.activeSuggestion = -1;
        localThis.orderByField = "variantId";
        localThis.reverseSort = false;

        localThis.coverage = {};
        localThis.coverage.region = {"start":null,
                                     "stop":null,
                                     "chrom":null,
                                     "exons":[],
                                    };
        localThis.coverage.zoom = "overview";
        localThis.coverage.function = "mean";
        localThis.coverage.coverageMetric = "mean";
        localThis.coverage.overValue = 50;
        localThis.coverage.includeUTR = true;
        localThis.coverage.data = [];
        localThis.coverage.update = 0;
        localThis.variants = [];
        localThis.updatedOverValue = updatedOverValue;

        localThis.item = null;
        localThis.itemType = null;

        localThis.browserLink = browserLink;
        localThis.dataset = {"shortName": $routeParams.dataset};

        // search functions
        localThis.search = search;
        localThis.autocomplete = autocomplete;

        // variant list functions
        localThis.filterVariants = filterVariants;
        localThis.reorderVariants = reorderVariants;
        localThis.filterVariantsBy = "all";
        localThis.filterIncludeNonPass = false;

        // variant list frequency box thresholds
        localThis.variantBoxThresholds = [0, 1/10000, 1/1000, 1/100, 1/20, 1/2];

        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
            });
	    
            if ($routeParams.transcript) {
                localThis.itemType = "transcript";
                localThis.item = $routeParams.transcript;
                Browser.getTranscript($routeParams.dataset, $routeParams.version, $routeParams.transcript).then( function(data) {
                    localThis.transcript = data.transcript;
                    localThis.gene       = data.gene;
                    localThis.coverage.region.exons = data.exons;
                });
            }
            if ($routeParams.region) {
                localThis.itemType = "region";
                localThis.item = $routeParams.region;
                Browser.getRegion($routeParams.dataset, $routeParams.version, $routeParams.region)
		    .then( function(data) {
			localThis.region = data.region;
                    })
		    .catch((err) => {
			localThis.region = {"statusCode": err.status,
					    "statusText": err.statusText,
					    "variantId": $routeParams.region};
		    });
            }
            if ($routeParams.gene) {
                localThis.itemType = "gene";
                localThis.item = $routeParams.gene;
                Browser.getGene($routeParams.dataset, $routeParams.version, $routeParams.gene).then( function(data) {
                    localThis.gene = data.gene;
                    localThis.transcripts = data.transcripts;
                    localThis.coverage.region.exons = data.exons;
                });
            }
           if (localThis.itemType) {
               Browser.getVariants($routeParams.dataset, $routeParams.version, localThis.itemType, localThis.item)
		   .then( function(data) {
                       localThis.variants = data.variants;
                       localThis.headers = data.headers;

                       // TODO Move to function later
                       let mapFunction = function(variant) {
                           variant.isPass     = variant.filter == "PASS";
                           variant.isLof      = variant.flags == "LC LoF";
                           variant.isMissense = variant.majorConsequence == "missense";
                       };
                       localThis.variants.map(mapFunction);

                       localThis.filteredVariants();
                   })
	       	   .catch((err) => {
		       localThis.variants = {"statusCode": err.status,
					     "statusText": err.statusText};
		       localThis.filteredVariants = "done";
		   });
                Browser.getCoveragePos($routeParams.dataset, $routeParams.version, localThis.itemType, localThis.item).then( function(data) {
                    localThis.coverage.region.start = data.start;
                    localThis.coverage.region.stop  = data.stop;
                    localThis.coverage.region.chrom = data.chrom;
                });
               Browser.getCoverage($routeParams.dataset, $routeParams.version, localThis.itemType, localThis.item)
		   .then(function(data) {
                       localThis.coverage.data = data.coverage;
                       localThis.coverage.loaded = true;
                   })
		   .catch((err) => {
		       localThis.coverage = {"statusCode": err.status,
					     "statusText": err.statusText,
					     "loaded": true};
		   });
            }
            if ($routeParams.variant) {
                Browser.getVariant($routeParams.dataset, $routeParams.version, $routeParams.variant).then( function(data) {
                    localThis.variant = data.variant;
                });
            }
            Dataset.getDataset($routeParams.dataset, $routeParams.version, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                },
                function(error) {
                    localThis.error = error;
            });

        }

        function browserLink(link) {
            if ( $routeParams.version ) {
                return "/dataset/" + $routeParams.dataset + "/version/" + $routeParams.version + "/browser/" + link;
            }
            return "/dataset/" + $routeParams.dataset + "/browser/" + link;
        }

        function search(query) {
            if (query) {
                localThis.query = query;
            }
            if (localThis.query) {
                Browser.search($routeParams.dataset, $routeParams.version, localThis.query).then( function(data) {

                    var url = browserLink(`${data.type}/${data.value}`);
                    if ( data.type == "error" || data.type == "not_found" ) {
                        url = browserLink("not_found");
                    }
                    $window.location.href = url;
                });
            }
        }

        function autocomplete() {
            localThis.activeSuggestion = -1;
            if (localThis.query) {
                Browser.autocomplete($routeParams.dataset, $routeParams.version, localThis.query)
                       .then( function(data) {
                            localThis.suggestions = data.values;
                        });
            } else {
                localThis.suggestions = [];
            }
        }

        function filterVariants() {
            let filterAsText = localThis.filterVariantsBy + localThis.filterIncludeNonPass;
            if (localThis.filterVariantsOld == filterAsText) {
                return;
            }
            localThis.filterVariantsOld = filterAsText;

            let filterFunction = function(variant) {
                // Remove variants that didn't PASS QC
                if (! (localThis.filterIncludeNonPass || variant.isPass )) {
                    return false;
                }
                switch(localThis.filterVariantsBy) {
                    case "all":
                        return true;
                    case "lof":
                        return variant.isLof;
                    case "mislof":
                        return variant.isLof || variant.isMissense;
                    default:
                        return false;
                }
            };

            localThis.filteredVariants = localThis.variants.filter( filterFunction );
            localThis.coverage.update += 1;
        }

        function reorderVariants(field) {
            if (field == localThis.orderByField ) {
                localThis.reverseSort = !localThis.reverseSort;
            }
            localThis.orderByField = field;
        }

        function updatedOverValue() {
            localThis.coverage.coverageMetric = "over";
        }
    }]);
})();
