(function() {
    angular.module("App")
    .factory("CoveragePlot", [function() {

        var settings = {"fontSize": 12,
                        "spacing": 4,
                        "annotationSpace": 50,
                        "margins":{"t":0, "r":0, "b":0, "l":0},
                        };

        return {
            drawAnnotation: drawAnnotation,
            drawGrid:       drawGrid,
            plotData:       plotData,
            settings:       settings,
        };

        function nextColor(num) {
            const r = Math.round( num % 255 );
            const g = Math.round((num / 255) % 255);
            const b = Math.round((num / (255*255)) % 255);
            return `rgb(${r},${g},${b})`;
        }

        function drawAnnotation(ctx, hit, colorHash, variants, axes, exons) {
            var plotHeight = settings.annotationSpace;
            var t = ctx.canvas.clientHeight - settings.margins.t - plotHeight + settings.spacing + settings.fontSize;
            var h = plotHeight / 2.0;                    // half plot height
            var w = ctx.canvas.clientWidth - settings.margins.l - settings.margins.r; // plot width
            var r = axes.x.stop - axes.x.start;                     // region length
            var s = 5;                                              // min size of variant blips
            var connectExons = false;
            var connectABitAnyway = true;

            var colorNumber = 1;

            // Draw exons
            if (exons) {
                var lastX = 0
                for (var i = 0; i < exons.length; i++) {
                    if (exons[i].type == "exon") {
                        continue
                    }
                    var x = settings.margins.l + w * (exons[i].start - axes.x.start)/r;
                    var l = w * (exons[i].stop - exons[i].start)/r;
                    var M = (connectExons ? h-s/2.0-2 : h);
                    var H = h;
                    ctx.fillStyle = "#a96500"
                    if (exons[i].type == "UTR") {
                        H = h*.5;
                        ctx.fillStyle = "#0047b2"
                    }

                    if ( x < settings.margins.l )
                        continue;

                    // Add hit area for exon
                    hit.beginPath();
                    var hitColor = nextColor(colorNumber);  // unique color
                    hit.fillStyle = hitColor;
                    hit.fillRect(x,t+h-H,l,H*2);
                    colorHash[hitColor] = exons[i].type + ": " + exons[i].start + "-" + exons[i].stop;
                    colorNumber++;
                    hit.closePath();

                    // draw exon rectangles
                    ctx.globalAlpha = 0.2;
                    ctx.beginPath();
                    ctx.fillRect(x,t+h-H,l,H*2);
                    ctx.closePath();

                    // exon outline
                    ctx.globalAlpha = 0.5;
                    // top part
                    ctx.beginPath();

                    if (connectExons) {
                        ctx.moveTo(lastX,t+M); // start of plot, or last position
                        ctx.lineTo(x,t+M);
                    } else {
                        ctx.moveTo(x,t+M);
                    }
                    ctx.lineTo(x,t+h-H);
                    ctx.lineTo(x+l,t+h-H);
                    ctx.lineTo(x+l,t+M);
                    ctx.stroke();

                    ctx.closePath();

                    // bottom part
                    ctx.beginPath();

                    if (connectExons) {
                        M = h+s/2.0+2;
                        ctx.moveTo(lastX,t+M);
                        ctx.lineTo(x,t+M);
                    } else {
                        ctx.moveTo(x,t+M);
                    }

                    ctx.lineTo(x,t+h+H);
                    ctx.lineTo(x+l,t+h+H);
                    ctx.lineTo(x+l,t+M);
                    ctx.stroke();

                    ctx.closePath();

                    if (!connectExons && connectABitAnyway && lastX != 0) {
                        ctx.beginPath();
                        ctx.moveTo(lastX, t+M);
                        ctx.lineTo(x, t+M);
                        ctx.stroke();
                        ctx.closePath();
                    }

                    lastX = x+l;
                }
            }

            ctx.globalAlpha = 0.4;
            if (variants == undefined) {
                variants = [];
            }
            for (var i = 0; i < variants.length; i++) {
                if ( variants[i].pos < axes.x.start || variants[i].pos > axes.x.stop)
                    continue;
                var x = settings.margins.l + w * (variants[i].pos - axes.x.start)/r;
                var height = Math.max(s, h*2.0*variants[i].alleleFreq)

                if ( x < settings.margins.l )
                    continue;

                ctx.beginPath();
                // Verbose just to be clear
                switch (variants[i].majorConsequence) {
                case "upstream gene":               ctx.fillStyle="#157e28"; break;
                case "5'UTR":                       ctx.fillStyle="#0047b2"; break;
                case "inframe insertion":           ctx.fillStyle="#a96500"; break;
                case "inframe deletion":            ctx.fillStyle="#a96500"; break;
                case "missense":                    ctx.fillStyle="#a96500"; break;
                case "synonymous":                  ctx.fillStyle="#157e28"; break;
                case "intron":                      ctx.fillStyle="#157e28"; break;
                case "splice region":               ctx.fillStyle="#157e28"; break;
                case "non coding transcript exon":  ctx.fillStyle="#157e28"; break;
                case "3'UTR":                       ctx.fillStyle="#0047b2"; break;
                default:                            ctx.fillStyle="#ababab";
                }

                // Add hit area for variant
                hit.beginPath();
                var hitColor = nextColor(colorNumber);  // unique color
                hit.fillStyle = hitColor;
                hit.ellipse(x, t+h, 2, height*0.5, 0, 0, 2 * Math.PI);
                hit.fill();

                colorHash[hitColor] = `${variants[i].majorConsequence}<br>
                                       ${variants[i].chrom}:${variants[i].pos}
                                       ${variants[i].ref}->${variants[i].alt}<br>
                                       ${variants[i].HGVS}<br>
                                       Frequency: ${variants[i].alleleFreq}`;
                colorNumber++;
                hit.closePath();

                ctx.ellipse(x, t+h, 2, height*0.5, 0, 0, 2 * Math.PI);
                // ctx.rect(x-2,h-height/2.0,5,height);
                ctx.fill();
                ctx.closePath();
            }

            // Reset context values
            ctx.strokeStyle = "#000000"
            ctx.fillStyle = "#000000"
            ctx.globalAlpha = 1.0;
        }

        function drawGrid(ctx, axes, region, includeUTR) {
            // Set margins
            var width = 0;
            for (var i = 0; i < axes.y.length; i++) {
                // 3 pixels extra for antialiasing
                width = ctx.measureText(axes.y[i]).width + 3 + settings.spacing;
                if (width > settings.margins.l)
                    settings.margins.l = width;
            }
            settings.margins.b = settings.fontSize + settings.spacing + settings.annotationSpace;
            settings.margins.t = settings.fontSize + settings.spacing;

            // Set convenience variables
            let h = ctx.canvas.clientHeight;
            let w = ctx.canvas.clientWidth;
            let t = settings.margins.t;
            let r = settings.margins.r;
            let b = settings.margins.b;
            let l = settings.margins.l;
            var step = (h-b-t)/(axes.y.length-1);

            // Clear entire canvas
            ctx.clearRect(0, 0, w,h);

            // Set context font
            ctx.font=`${settings.fontSize}px Arial`;

            // Draw coverage axis (y) text
            ctx.fillStyle="#000000";
            for (var i = 0; i < axes.y.length; i++) {
                var width = ctx.measureText(axes.y[i]).width;
                ctx.fillText(axes.y[i], l - width - settings.spacing, h-step*i+(settings.fontSize/2.0-1) - b)
            }

            // Draw position axis (x) text
            if (region.start) {
                ctx.fillStyle="#000000"
                ctx.fillText(axes.x.start, l + settings.spacing/2.0, h-b+settings.spacing/2.0+settings.fontSize)
            }
            if (region.stop) {
                ctx.fillStyle="#000000"
                var width = ctx.measureText(axes.x.stop).width;
                ctx.fillText(axes.x.stop, w-width-settings.spacing/2.0, h-b+settings.spacing/2.0+settings.fontSize)
            }

            // Set convenience variables
            var pw = w-l-r; // plot width
            var ph = h-b-t; // plot height - from text size

            // Draw plot background
            ctx.beginPath();
            ctx.fillStyle="#fafafa";
            ctx.fillRect(l, t, pw, ph); 
            ctx.closePath();

            // Draw axes.y grid
            ctx.beginPath();
            ctx.moveTo(l, t);
            ctx.lineTo(l, h - b + settings.spacing/2.0);
            ctx.stroke();
            ctx.closePath();
            for (var i = 0; i < axes.y.length; i++) {
                var width = ctx.measureText(axes.y[i]).width;
                ctx.beginPath();
                ctx.strokeStyle = "#000000";
                ctx.lineWidth = 1;

                ctx.moveTo(l - settings.spacing*0.5, h-step*i - b)
                ctx.lineTo(l + settings.spacing*0.5, h-step*i - b)
                ctx.stroke();
                ctx.closePath();

                ctx.beginPath();
                if (i == 0) {
                    ctx.lineWidth = 1;
                    ctx.strokeStyle = "#000000";
                } else if ( axes.y[i]%50 == 0 ) {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#505050";
                } else if ( i%2 == 0 ) {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#b0b0b0";
                } else {
                    ctx.lineWidth = .5;
                    ctx.strokeStyle = "#e0e0e0";
                }

                ctx.moveTo(l + settings.spacing*0.5, h-step*i - b)
                ctx.lineTo(w-r, h-step*i - b);
                ctx.stroke();
                ctx.closePath();
            }

            // Guess a good number of horizontal splits
            var width = ctx.measureText(region.stop).width;
            var s = Math.floor( (pw / width) / 2.0) - 1;
            step = (region.stop-region.start) / s;

            for (var i = 1; i <= s; i++) {
                var label = Math.floor(region.start + i*step);
                var x = l + settings.spacing + i*pw/s;
                ctx.beginPath();
                ctx.strokeStyle = "#b0b0b0";
                ctx.lineWidth = .5;

                ctx.moveTo(x, t)
                ctx.lineTo(x, t+ph+settings.spacing*.5)
                ctx.stroke();
                ctx.closePath();

                if (i != s) {
                    ctx.fillStyle="#000000"
                    var labelWidth = ctx.measureText(label).width;
                    ctx.fillText(label, x-labelWidth/2.0, h-b+settings.spacing/2.0+settings.fontSize)
                }
            }
        }

        function plotData(ctx, data, axes) {
            var yMin = axes.y[0];
            var yMax = axes.y[axes.y.length-1];
            var width = ctx.canvas.clientWidth - settings.margins.l - settings.margins.r;
            var height = ctx.canvas.clientHeight - settings.margins.t - settings.margins.b;

            let xAxisLength = axes.x.stop - axes.x.start;
            let yAxisLength = yMax - yMin;

            var points = [];
            for (var p of data.data) {
                let x = settings.margins.l + width * (p.pos - axes.x.start) / xAxisLength;
                let y = settings.margins.t + height * (1 - (Math.max(yMin, Math.min(p[data.function], yMax)) - yMin) / yAxisLength);
                if (x < settings.margins.l || y === undefined)
                    continue

                points.push([x,y]);
            }

            // Draw the line and AUC
            ctx.beginPath();
            ctx.fillStyle = "rgba(102, 153, 204, 0.3)";
            ctx.strokeStyle = "rgba(0, 102, 153, 0.8)";

            ctx.moveTo(points[0][0], settings.margins.t + height);
            for (let p of points) {
                ctx.lineTo(p[0],p[1]);
            }
            ctx.lineTo(points[points.length-1][0], settings.margins.t + height);
            ctx.stroke();
            ctx.fill();
            ctx.closePath();

            // Add graph line blips
            if (Math.abs(points[0][0] - points[1][0]) > 4) {
                ctx.beginPath();
                for (p of points) {
                    let [x, y] = p;
                    ctx.moveTo(x, y-2);
                    ctx.lineTo(x, y+2);
                }
                ctx.stroke();
                ctx.closePath();
            }

            // Reset context values
            ctx.strokeStyle = "#000000"
            ctx.fillStyle = "#000000"
        }

    }]);
})();
