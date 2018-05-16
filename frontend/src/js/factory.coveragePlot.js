(function() {
    angular.module("App")
    .factory("CoveragePlot", [function() {
        return {
            drawGrid: drawGrid,
            plotData: plotData,
        };

        function drawGrid(ctx, axis, pos) {
            // Set basic variables
            let h = ctx.canvas.clientHeight;
            let w = ctx.canvas.clientWidth;
            var fontSize = 16;
            var spacing = 6;
            var l = 0;  // left margin, calculated later from axis text size
            var r = 0;  // right, margin, unused
            var b = fontSize + spacing; // bottom margin, from text size
            var t = fontSize + spacing;
            var step = (h-b-t)/(axis.length-1);
            ctx.font=`${fontSize}px Arial`;

            // Clear entire canvas
            ctx.clearRect(0, 0, w,h);

            // Set header text
            if (pos.chrom) {
                ctx.fillStyle="#000000"
                var text = `Chrom ${pos.chrom}`;
                var width = ctx.measureText(text).width;
                ctx.fillText(text, w/2.0-width/2.0, fontSize+spacing/2.0)
            }

            // Draw coverage axis text
            ctx.fillStyle="#000000";
            for (var i = 0; i < axis.length; i++) {
                var width = ctx.measureText(axis[i]).width;
                if (width > l)
                    l = width;
            }
            for (var i = 0; i < axis.length; i++) {
                var width = ctx.measureText(axis[i]).width;
                ctx.fillText(axis[i], l - width, h-step*i+(fontSize/2.0-1) - b)
            }

            // Draw position axis text
            if (pos.start) {
                ctx.fillStyle="#000000"
                ctx.fillText(pos.start, l + spacing/2.0, h-spacing/2.0)
            }
            if (pos.stop) {
                ctx.fillStyle="#000000"
                var width = ctx.measureText(pos.stop).width;
                ctx.fillText(pos.stop, w-width-spacing/2.0, h-spacing/2.0)
            }

            // Set convenience variables
            var pw = w-l-r-spacing; // plot width
            var ph = h-b-t; // plot height - from text size
            // Draw plot background
            ctx.beginPath();
            ctx.fillStyle="#fafafa";
            ctx.fillRect(l + spacing, t, pw, ph); 
            ctx.closePath();

            // Draw axis grid
            ctx.beginPath();
            ctx.moveTo(l + spacing, t);
            ctx.lineTo(l + spacing, h - b + spacing/2.0);
            ctx.stroke();
            ctx.closePath();
            for (var i = 0; i < axis.length; i++) {
                var width = ctx.measureText(axis[i]).width;
                ctx.beginPath();
                ctx.strokeStyle = "#000000";
                ctx.lineWidth = 1;

                ctx.moveTo(l + spacing*1.5, h-step*i - b)
                ctx.lineTo(l + spacing*0.5, h-step*i - b)
                ctx.stroke();
                ctx.closePath();

                ctx.beginPath();
                if (i == 0) {
                    ctx.lineWidth = 1;
                    ctx.strokeStyle = "#000000";
                } else if ( axis[i]%50 == 0 ) {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#505050";
                } else if ( i%2 == 0 ) {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#b0b0b0";
                } else {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#e0e0e0";
                }

                ctx.moveTo(l + spacing*1.5, h-step*i - b)
                ctx.lineTo(w-r, h-step*i - b);
                ctx.stroke();
                ctx.closePath();
            }

            // Guess a good number of horizontal splits
            var width = ctx.measureText(pos.stop).width;
            var s = Math.floor( (pw / width) / 2.0) - 1;
            step = (pos.stop-pos.start) / s;

            for (var i = 1; i <= s; i++) {
                var label = Math.floor(pos.start + i*step);
                var x = l + spacing + i*pw/s;
                ctx.beginPath();
                ctx.strokeStyle = "#b0b0b0";
                ctx.lineWidth = .5;

                ctx.moveTo(x, t)
                ctx.lineTo(x, t+ph+spacing*.5)
                ctx.stroke();
                ctx.closePath();

                if (i != s) {
                    ctx.fillStyle="#000000"
                    var labelWidth = ctx.measureText(label).width;
                    ctx.fillText(label, x-labelWidth/2.0, h-spacing/2.0)
                }
            }

            return {"x":l + spacing, "y":t, "width":pw, "height":ph};
        }

        function plotData(ctx, plotArea, data, type) {
            var yMin = data.axis[0];
            var yMax = data.axis[data.axis.length-1];

            var first = true;
            ctx.beginPath();
            ctx.strokeStyle = "#006699"
            for (var i = 0; i < data.data.length; i++) {
                var x = plotArea.x + plotArea.width *(data.data[i].pos - data.pos.start) / (data.pos.stop - data.pos.start)
                var y = plotArea.y + plotArea.height * (1-(Math.min(data.data[i][data.function], yMax) - yMin) / (yMax-yMin));
                if (x < 0 || y === undefined)
                    continue
                if (first) {
                    first = false;
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            ctx.closePath();

            first = true;
            var lastX = 0;
            ctx.beginPath();
            ctx.globalAlpha=0.3;
            ctx.fillStyle = "#6699cc"
            for (var i = 0; i < data.data.length; i++) {
                var x = plotArea.x + plotArea.width *(data.data[i].pos - data.pos.start) / (data.pos.stop - data.pos.start)
                var y = plotArea.y + plotArea.height * (1-(Math.min(data.data[i][data.function], yMax) - yMin) / (yMax-yMin));
                if (x < 0 || y === undefined)
                    continue
                ctx.fillRect(x,y,1,plotArea.y + plotArea.height - y);
            }
            ctx.closePath();

            // Reset context values
            ctx.strokeStyle = "#000000"
            ctx.fillStyle = "#000000"
            ctx.globalAlpha = 1.0;
        }

    }]);
})();
