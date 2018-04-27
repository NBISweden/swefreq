(function() {
    angular.module("App")
    .factory("browserGene", ["$http", function($http) {
        return {
            getGene: getGene,
        };

        function getGene(dataset, gene) {
            return $http.get("/api/datasets/" + dataset + "/browser/gene/" + gene).then(function(data) {
                return data.data;
            });
        }
    }]);
})();
