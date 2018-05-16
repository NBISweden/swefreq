(function() {
    angular.module("App")
    .directive("coverage", ["CoveragePlot", "Browser", function (CoveragePlot) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var ctx = element[0].getContext('2d');

                scope.$watch('coverage', function(newValue, oldValue) {
                    if (newValue) {
                        var plotArea = CoveragePlot.drawGrid(ctx, newValue.axis, newValue.pos);
                        if ( newValue.data != oldValue.data ) {
                            CoveragePlot.plotData(ctx, plotArea, newValue);
                        }
                    }
                }, true);
            }
            
        };
    }]);
})();
