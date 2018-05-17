(function() {
    angular.module("App")
    .directive("coverage", ["CoveragePlot", function (CoveragePlot) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var ctx = element[0].getContext('2d');

                scope.$watch('data.coverage', function(newValue, oldValue) {
                    if (newValue) {
                        var margins = CoveragePlot.drawGrid(ctx, scope.data.plot, scope.data.region);
                        scope.data.plot.margins = margins;

                        if ( newValue.data != oldValue.data ) {
                            CoveragePlot.plotData(ctx, newValue, scope.data.region, scope.data.plot);
                        }
                    }
                }, true);
            }
            
        };
    }]);
})();
