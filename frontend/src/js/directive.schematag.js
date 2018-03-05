(function() {
    angular.module("App")
    .directive("schematag", ["$sce", "$filter", function ($sce, $filter) {
        return {
            restrict: "EA",
            link: function (scope, element) {
                scope.$watch("ld", function (val) {
                    if (val) {
                        val = $sce.trustAsHtml($filter("json")(val));
                        element[0].innerHTML = "<script type=\"application/ld+json\">"+ val + "</script>";
                    }
                });
            }
        };
    }]);
})();