(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "$window", "User", "Dataset", "Browser",
                             function( $routeParams,   $window,   User,   Dataset,   Browser) {
        var localThis = this;
        localThis.search = {"query":"", "autocomplete":[]};
        localThis.orderByField = 'variantId';
        localThis.reverseSort = false;
        localThis.coverage = {};
        localThis.coverage.region = {"start":null,
                                     "stop":null,
                                     "chrom":null,
                                     "exons":[],
                                    };
        localThis.coverage.zoom = "overview";
        localThis.coverage.function = "mean";
        localThis.coverage.includeUTR = true;
        localThis.coverage.data = [];
        localThis.coverage.update = 0;
        localThis.variants = []

        localThis.item = null;
        localThis.itemType = null;

        localThis.browserLink = browserLink;
        localThis.dataset = {'shortName':$routeParams.dataset};

        // search functions
        localThis.search = search;
        localThis.autocomplete = autocomplete;

        // coverage functions
        localThis.setCoverageZoom = setCoverageZoom;

        // variant list functions
        localThis.filterVariantsBy = filterVariantsBy;
        localThis.reorderVariants = reorderVariants;

        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
            });

            if ($routeParams.transcript) {
                localThis.itemType = "transcript";
                localThis.item = $routeParams.transcript
                Browser.getTranscript($routeParams.dataset, $routeParams.transcript).then( function(data) {
                    localThis.transcript = data.transcript;
                    localThis.gene       = data.gene;
                });
            }
            if ($routeParams.region) {
                localThis.itemType = "region";
                localThis.item = $routeParams.region;
                Browser.getRegion($routeParams.dataset, $routeParams.region).then( function(data) {
                    localThis.region = data.region;
                });
            }
            if ($routeParams.gene) {
                localThis.itemType = "gene";
                localThis.item = $routeParams.gene;
                Browser.getGene($routeParams.dataset, $routeParams.gene).then( function(data) {
                    localThis.gene = data.gene;
                    localThis.transcripts = data.transcripts;
                    localThis.coverage.region.exons = data.exons;
                });
            }
            if (localThis.itemType) {
                Browser.getVariants($routeParams.dataset, localThis.itemType, localThis.item).then( function(data) {
                    localThis.variants = data.variants;
                    localThis.filteredVariants = data.variants;
                    localThis.headers = data.headers;
                    Browser.getCoveragePos($routeParams.dataset, localThis.itemType, localThis.item).then( function(data) {
                        localThis.coverage.region.start = data.start;
                        localThis.coverage.region.stop  = data.stop;
                        localThis.coverage.region.chrom = data.chrom;
                        Browser.getCoverage($routeParams.dataset, localThis.itemType, localThis.item).then(function(data) {
                            localThis.coverage.data = data.coverage;
                        });
                    });
                });
            }
            if ($routeParams.variant) {
                Browser.getVariant($routeParams.dataset, $routeParams.variant).then( function(data) {
                    localThis.variant = data.variant;
                });
            }
            Dataset.getDataset($routeParams.dataset, $routeParams.version)
                .then(function(data) {
                    localThis.dataset = data.dataset;
                },
                function(error) {
                    localThis.error = error;
            });
        }

        function browserLink(link) {
            return "/dataset/" + $routeParams.dataset + "/browser/" + link;
        }

        function search(query) {
            if (query) {
                localThis.search.query = query;
            }
            if (localThis.search.query) {
                Browser.search($routeParams.dataset, localThis.search.query).then( function(data) {
                    if (data.redirect) {
                        $window.location.href = data.redirect;
                    }
                })
            }
        }

        function autocomplete() {
            if (localThis.search.query) {
                Browser.autocomplete($routeParams.dataset, localThis.search.query)
                       .then( function(data) {
                            localThis.search.autocomplete = data.values;
                        });
            } else {
                localThis.search.autocomplete = [];
            }
        }

        function setCoverageZoom($event) {
            let clickedElement = $event.target || $event.srcElement;

            if( clickedElement.nodeName === "BUTTON" ) {

              let activeButton = clickedElement.parentElement.querySelector(".active");
              // if a Button already has Class: .active
              if( activeButton ) {
                activeButton.classList.remove("active");
              }

              clickedElement.className += " active";
            }
            let zoomLevel = clickedElement.value;
            localThis.coverage.zoom = zoomLevel;
        }

        function filterVariantsBy($event) {
            let clickedElement = $event.target || $event.srcElement;

            if( clickedElement.nodeName === "BUTTON" ) {

              let activeButton = clickedElement.parentElement.querySelector(".active");
              // if a Button already has Class: .active
              if( activeButton ) {
                activeButton.classList.remove("active");
              }

              clickedElement.className += " active";
            }
            let filters = angular.fromJson(clickedElement.value);
            if (!Array.isArray(filters) || filters.length == 0) {
                localThis.filteredVariants = localThis.variants;
            } else {
                localThis.filteredVariants = []
                for (var i = 0; i < filters.length; i++) {
                    var filter = filters[i];
                    for (var j = 0; j < localThis.variants.length; j++) {
                        var variant = localThis.variants[j];
                        if (variant.majorConsequence == filter) {
                            localThis.filteredVariants.push(variant);
                        }
                    }
                }
            }
            localThis.coverage.update += 1;
        }

        function reorderVariants(field) {
            if (field == localThis.orderByField ) {
                localThis.reverseSort = !localThis.reverseSort;
            }
            localThis.orderByField = field;
        }

    }]);
})();
