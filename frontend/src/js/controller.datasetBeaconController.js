(function() {
    angular.module('App')
    .controller('datasetBeaconController', ['$http', '$routeParams', 'Beacon', 'Dataset', 'User',
                                function($http, $routeParams, Beacon, Dataset, User) {
        var localThis = this;
        var dataset = $routeParams["dataset"];
        localThis.queryResponses = [];

        Beacon.getBeaconReferences(dataset).then(
                function(data) {
                    localThis.references = data;
                }
            );

        User().then(function(data) {
            localThis.user = data.data;
        });

        Dataset($routeParams['dataset'], $routeParams['version']).then(function(data){
                localThis.dataset = data.dataset;
            },
            function(error) {
                localThis.error = error;
            });

        localThis.search = function() {
            Beacon.queryBeacon(localThis).then(function (response) {
                    d = response.data;
                    d.query.position += 1; // Beacon is 0-based
                    d.response.state = d.response.exists ? 'Present' : 'Absent';
                    localThis.queryResponses.push(d);
                },
                function (response){
                    localThis.queryResponses.push({
                        'response': { 'state': 'Error' },
                        'query': {
                            'chromosome':      localThis.chromosome,
                            'position':        localThis.position,
                            'allele':          localThis.allele,
                            'referenceAllele': localThis.referenceAllele,
                            'reference':       localThis.reference
                        }
                    });
                });
        };
    }]);
})();
