(function() {
    angular.module("App")
    .directive("annotation", ["CoveragePlot", function (CoveragePlot) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var ctx = element[0].getContext('2d');

                scope.$watch('data.variants', function(newValue, oldValue) {
                    if (newValue.data) {
                        CoveragePlot.drawAnnotation(ctx, newValue.data, scope.data.plot.margins, scope.data.region);
                    }
                }, true);
            }

        };
    }]);
})();
