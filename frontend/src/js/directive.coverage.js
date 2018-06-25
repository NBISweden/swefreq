(function() {
    angular.module("App")
    .directive("coverage", ["CoveragePlot", function (CoveragePlot) {
        return {
            restrict: "A",
            link: function(scope, element) {
                var ctx = element[0].getContext("2d");

                // Create hit-canvas for mouseover annotations
                const hitCanvas = document.createElement("canvas");
                hitCanvas.width  = ctx.canvas.clientWidth;
                hitCanvas.height = ctx.canvas.clientHeight;
                const hitCtx = hitCanvas.getContext("2d");
                const colorHash = {};

                element[0].addEventListener("mousemove", (e) => {
                    var rect = element[0].getBoundingClientRect();
                    const pos = {
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top
                    };
                    const pixel = hitCtx.getImageData(pos.x, pos.y, 1, 1).data;
                    const color = `rgb(${pixel[0]},${pixel[1]},${pixel[2]})`;
                    const item = colorHash[color];

                    var infoPanel = document.getElementById("annotationPanel");
                    var info = document.getElementById("annotationInfo");
                    var offset = {"x":-5, "y":20};

                    if (item) {
                        info.innerHTML = item;
                        let p = {"x":pos.x+offset.x, "y":pos.y+offset.y};

                        infoPanel.style.top = `${p.y}px`;
                        infoPanel.style.left = `${p.x}px`;
                        infoPanel.style.zIndex = 10;
                        infoPanel.style.visibility = "visible";
                    } else {
                        infoPanel.style.visibility = "hidden";
                    }
                });

                scope.$watch("ctrl.coverage", function(newValue) {
                    // Update the coverage function
                    if ( newValue.coverageMetric == "over" ) {
                        newValue.function = newValue.overValue;
                    }
                    else {
                        newValue.function = newValue.coverageMetric;
                    }

                    // set zoom level
                    var width = element[0].parentElement.clientWidth;
                    if (newValue.zoom == "detail") {
                        //TODO: We should check if this is set, but for now I don't
                        var margin = CoveragePlot.settings.margins.l;
                        width = Math.max(width, newValue.data.length + margin);
                    }
                    element[0].width = width;
                    hitCanvas.width  = width;

                    // Set axes
                    var axes = {"x":{"start":0, "end":0},
                                "y":[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]};

                    // Figure out x-axis limits
                    axes.x.start = newValue.region.start;
                    axes.x.stop  = newValue.region.stop;
                    if (!newValue.includeUTR) {
                        var first = true;
                        for (var i = 0; i < newValue.region.exons.length; i++) {
                            if (newValue.region.exons[i].type == "UTR") {
                                if (first) {
                                    axes.x.start = newValue.region.exons[i].stop;
                                    first = false;
                                } else {
                                    axes.x.stop  = newValue.region.exons[i].start;
                                }
                            }
                        }
                    }

                    // Figure out y-axis limits
                    if (Number.isInteger(newValue.function)) {
                        axes.y = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
                    } else {
                        axes.y = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
                    }

                    if (newValue.data.length > 0) {
                        CoveragePlot.drawGrid(ctx, axes, newValue.region, newValue.includeUTR);

                        CoveragePlot.plotData(ctx, newValue, axes);

                        var variants = scope.$parent.$parent.ctrl.filteredVariants;
                        CoveragePlot.drawAnnotation(ctx, hitCtx, colorHash, variants, axes, newValue.region.exons);
                    }
                }, true);
            }
            
        };
    }]);
})();
