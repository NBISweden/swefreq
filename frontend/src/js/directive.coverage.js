(function() {
    angular.module("App")
    .directive("coverage", ["CoveragePlot", function (CoveragePlot) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var ctx = element[0].getContext('2d');
                const hitCanvas = document.createElement('canvas');

                hitCanvas.width  = ctx.canvas.clientWidth;
                hitCanvas.height = ctx.canvas.clientHeight;

                const hitCtx = hitCanvas.getContext('2d');
                const colorHash = {};

                element[0].addEventListener('mousemove', (event) => {
                    var rect = element[0].getBoundingClientRect();
                    const pos = {
                        x: event.clientX - rect.left,
                        y: event.clientY - rect.top
                    };
                    const pixel = hitCtx.getImageData(pos.x, pos.y, 1, 1).data;
                    const color = `rgb(${pixel[0]},${pixel[1]},${pixel[2]})`;
                    const item = colorHash[color];

                    if (item) {
                        console.log(item)
                    }
                });

                scope.$watch("ctrl.coverage", function(newValue, oldValue) {
                    if (newValue.data.length > 0) {
                        var margins = CoveragePlot.drawGrid(ctx, newValue.axis, newValue.region);

                        CoveragePlot.plotData(ctx, newValue, margins);

                        var variants = scope.$parent.$parent.ctrl.variants;
                        CoveragePlot.drawAnnotation(ctx, hitCtx, colorHash, variants, margins, newValue.region);
                    }
                }, true);
            }
            
        };
    }]);
})();
