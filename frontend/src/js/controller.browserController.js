(function() {
    angular.module("App")
    .controller("browserController", ["$routeParams", "$scope", "$window", "User", "Dataset", "Browser",
                             function( $routeParams,   $scope,   $window,   User,   Dataset,   Browser) {
        $scope.search = {"query":"", "autocomplete":[]};
        $scope.orderByField = 'variantId';
        $scope.reverseSort = false;

        var localThis = this;
        localThis.browserLink = browserLink;
        localThis.dataset = {'shortName':$routeParams.dataset};
        // search functions
        localThis.search = search;
        localThis.autocomplete = autocomplete;
        // variant list functions
        localThis.filterVariantsBy = filterVariantsBy;
        localThis.downloadCSV = downloadCSV;
        localThis.reorderVariants = reorderVariants;
        activate();

        function activate() {
            User.getUser().then(function(data) {
                localThis.user = data;
            });
            if ($routeParams.transcript) {
                Browser.getTranscript($routeParams.dataset, $routeParams.transcript).then( function(data) {
                    localThis.transcript = data.transcript;
                    localThis.gene       = data.gene;
                });
                Browser.getVariants($routeParams.dataset, "transcript", $routeParams.transcript).then( function(data) {
                    localThis.variants = data.variants;
                    localThis.filteredVariants = data.variants;
                    localThis.headers = data.headers;
                });
            }
            if ($routeParams.region) {
                Browser.getRegion($routeParams.dataset, $routeParams.region).then( function(data) {
                    localThis.region = data.region;
                });
                Browser.getVariants($routeParams.dataset, "region", $routeParams.region).then( function(data) {
                    localThis.variants = data.variants;
                    localThis.filteredVariants = data.variants;
                    localThis.headers = data.headers;
                });
            }
            if ($routeParams.gene) {
                Browser.getGene($routeParams.dataset, $routeParams.gene).then( function(data) {
                    localThis.gene = data.gene;
                    localThis.transcripts = data.transcripts;
                });
                Browser.getVariants($routeParams.dataset, "gene", $routeParams.gene).then( function(data) {
                    localThis.variants = data.variants;
                    localThis.filteredVariants = data.variants;
                    localThis.headers = data.headers;
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
        }

        function downloadCSV() {
            alert("Sorry - Downloading not implemented yet.");
        }

        function reorderVariants(field) {
            if (field == $scope.orderByField ) {
                $scope.reverseSort = !$scope.reverseSort;
            }
            $scope.orderByField = field;
        }

    }]);
})();
