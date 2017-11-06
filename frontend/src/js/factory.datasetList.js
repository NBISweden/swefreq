(function() {
    angular.module("App")
    .factory("DatasetList", function($http, $q, $sce) {
        return {
            getDatasetList: getDatasetList,
        };

        function getDatasetList() {
            return $q(function(resolve,reject) {
                $http.get("/api/datasets").success(function(res){
                    var len = res.data.length;
                    var datasets = [];
                    for (var i = 0; i < len; i++) {
                        var d = res.data[i];
                        d.version.description = $sce.trustAsHtml(d.version.description);
                        if (d.future) {
                            d.urlbase = "/dataset/" + d.short_name + "/version/" + d.version.version;
                        }
                        else {
                            d.urlbase = "/dataset/" + d.short_name;
                        }

                        datasets.push(d);
                    }
                    resolve(datasets);
                });
            });
        };
    });
})();
