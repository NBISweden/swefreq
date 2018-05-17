(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "$scope", "$window", "User", "Dataset", "Browser",
                             function( $routeParams,   $scope,   $window,   User,   Dataset,   Browser) {
        $scope.search = {"query":"", "autocomplete":[]};
        $scope.orderByField = 'variantId';
        $scope.reverseSort = false;
        $scope.data = {};
        $scope.data.region   = {"start":null,
                                "stop":null,
                                "chrom":null
                               }
        $scope.data.plot =     {"axis":[0,10,20,30,40,50,60,70,80,90,100],
                                "margins":{'l':0, 'r':0, 't':0, 'b':0}
                               }
        $scope.data.coverage = {"function":"mean",
                                "individuals":30,
                                "data":[]
                               };
        $scope.data.variants = {"update":0,
                                "data":[]
                               };
        $scope.item = null;
        $scope.itemType = null;

        var localThis = this;
        localThis.browserLink = browserLink;
        localThis.dataset = {'shortName':$routeParams.dataset};

        // search functions
        localThis.search = search;
        localThis.autocomplete = autocomplete;

        // variant list functions
        localThis.filterVariantsBy = filterVariantsBy;
        localThis.reorderVariants = reorderVariants;

        // coverage functions
        localThis.updateCoverage = updateCoverage;

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
                });
            }
            if (localThis.itemType) {
                Browser.getVariants($routeParams.dataset, localThis.itemType, localThis.item).then( function(data) {
                    $scope.data.variants.data = data.variants;
                    localThis.filteredVariants = data.variants;
                    localThis.headers = data.headers;
                });
                Browser.getCoveragePos($routeParams.dataset, localThis.itemType, localThis.item).then( function(data) {
                    $scope.data.region = data;
                    localThis.coverage = true;
                    Browser.getCoverage($routeParams.dataset, localThis.itemType, localThis.item).then(function(data) {
                        $scope.data.coverage.data = data.coverage;
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
                $scope.search.query = query;
            }
            if ($scope.search.query) {
                Browser.search($routeParams.dataset, $scope.search.query).then( function(data) {
                    if (data.redirect) {
                        $window.location.href = data.redirect;
                    }
                })
            }
        }

        function autocomplete() {
            if ($scope.search.query) {
                Browser.autocomplete($routeParams.dataset, $scope.search.query)
                       .then( function(data) {
                            $scope.search.autocomplete = data.values;
                        });
            } else {
                $scope.search.autocomplete = [];
            }
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
                localThis.filteredVariants = $scope.data.variants.data;
            } else {
                localThis.filteredVariants = []
                for (var i = 0; i < filters.length; i++) {
                    var filter = filters[i];
                    for (var j = 0; j < $scope.data.variants.data.length; j++) {
                        var variant = $scope.data.variants.data[j];
                        if (variant.majorConsequence == filter) {
                            localThis.filteredVariants.push(variant);
                        }
                    }
                }
            }
        }

        function updateCoverage() {
            console.log("This function is currently not implemented");
        }

        function reorderVariants(field) {
            if (field == $scope.orderByField ) {
                $scope.reverseSort = !$scope.reverseSort;
            }
            $scope.orderByField = field;
        }

    }]);
})();
