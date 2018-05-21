(function() {
    angular.module("App")
    .factory("CoveragePlot", [function() {


        return {
            drawAnnotation: drawAnnotation,
            drawGrid:       drawGrid,
            plotData:       plotData,
        };

        function nextColor(num) {
            const r = Math.round( num % 255 );
            const g = Math.round((num / 255) % 255);
            const b = Math.round((num / (255*255)) % 255);
            return `rgb(${r},${g},${b})`;
        }

        function drawAnnotation(ctx, hit, colorHash, variants, margins, region) {
            var plotHeight = 50;
            var spacing = 22; // spacing + fontSize from plotGrid
            var t = ctx.canvas.clientHeight - margins.t - plotHeight + spacing;
            var h = plotHeight / 2.0;                    // half plot height
            var w = ctx.canvas.clientWidth - margins.l - margins.r; // plot width
            var r = region.stop - region.start;                     // region length
            var s = 5;                                              // min size of variant blips
            var connectExons = false;
            var connectABitAnyway = true;

            var colorNumber = 1;

            // debug blob.
            // The hit context is too small, but I haven't figured out how to enlarge it
            hit.beginPath();
            hit.fillStyle = "rgb(100,100,100)";
            hit.fillRect(0, 0, ctx.canvas.clientWidth, ctx.canvas.clientHeight);
            hit.closePath();

            // Draw exons
            if (region.exons) {
                var lastX = 0
                for (var i = 0; i < region.exons.length; i++) {
                    if (region.exons[i].type == "exon") {
                        continue
                    }
                    var x = margins.l + w * (region.exons[i].start - region.start)/r;
                    var l = w * (region.exons[i].stop - region.exons[i].start)/r;
                    var M = (connectExons ? h-s/2.0-2 : h);
                    var H = h;
                    ctx.fillStyle = "#a96500"
                    if (region.exons[i].type == "UTR") {
                        H = h*.5;
                        ctx.fillStyle = "#0047b2"
                    }

                    // Add hit area for exon
                    hit.beginPath();
                    var hitColor = nextColor(colorNumber);
                    hit.fillStyle = hitColor;
                    hit.fillRect(x,t+h-H,l,H*2);
                    // unique color
                    colorHash[hitColor] = region.exons[i].type + ": " + region.exons[i].start + "-" + region.exons[i].stop;
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
            for (var i = 0; i < variants.length; i++) {
                if ( variants[i].pos < region.start || variants[i].pos > region.stop)
                    continue;
                var x = margins.l + w * (variants[i].pos - region.start)/r;
                var height = Math.max(s, h*2.0*variants[i].alleleFreq)

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
                var hitColor = nextColor(colorNumber);
                hit.fillStyle = hitColor;
                hit.ellipse(x, t+h, 1, height*0.5, 0, 0, 2 * Math.PI);
                hit.fill();
                // unique color
                colorHash[hitColor] = variants[i].majorConsequence + "@" + variants[i].pos;
                colorNumber++;
                hit.closePath();

                ctx.ellipse(x, t+h, 1, height*0.5, 0, 0, 2 * Math.PI);
                // ctx.rect(x-2,h-height/2.0,5,height);
                ctx.fill();
                ctx.closePath();
            }

            // Reset context values
            ctx.strokeStyle = "#000000"
            ctx.fillStyle = "#000000"
            ctx.globalAlpha = 1.0;
        }

        function drawGrid(ctx, axis, region) {
            // Set basic variables
            let h = ctx.canvas.clientHeight;
            let w = ctx.canvas.clientWidth;
            let fontSize = 16;
            let spacing =  6;
            let annotationSpace = 50;
            var l = 0;  // left margin, calculated later from axis text size
            var r = 0;  // right, margin, unused
            var b = fontSize + spacing + annotationSpace; // bottom margin
            var t = fontSize + spacing;
            var step = (h-b-t)/(axis.length-1);
            ctx.font=`${fontSize}px Arial`;

            // Clear entire canvas
            ctx.clearRect(0, 0, w,h);

            // Set header text
            if (region.chrom) {
                ctx.fillStyle="#000000"
                var text = `Chrom ${region.chrom}`;
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
            if (region.start) {
                ctx.fillStyle="#000000"
                ctx.fillText(region.start, l + spacing/2.0, h-b+spacing/2.0+fontSize)
            }
            if (region.stop) {
                ctx.fillStyle="#000000"
                var width = ctx.measureText(region.stop).width;
                ctx.fillText(region.stop, w-width-spacing/2.0, h-b+spacing/2.0+fontSize)
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
            var width = ctx.measureText(region.stop).width;
            var s = Math.floor( (pw / width) / 2.0) - 1;
            step = (region.stop-region.start) / s;

            for (var i = 1; i <= s; i++) {
                var label = Math.floor(region.start + i*step);
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
                    ctx.fillText(label, x-labelWidth/2.0, h-b+spacing/2.0+fontSize)
                }
            }

            return {"l":l + spacing, "r":r, "b":b, "t":t};
        }

        function plotData(ctx, data, margins) {
            var yMin = data.axis[0];
            var yMax = data.axis[data.axis.length-1];
            var width = ctx.canvas.clientWidth - margins.l - margins.r;
            var height = ctx.canvas.clientHeight - margins.t - margins.b;

            var first = true;
            ctx.beginPath();
            ctx.strokeStyle = "#006699"
            for (var i = 0; i < data.data.length; i++) {
                var x = margins.l + width * (data.data[i].pos - data.region.start) / (data.region.stop - data.region.start)
                var y = margins.t + height * (1-(Math.min(data.data[i][data.function], yMax) - yMin) / (yMax-yMin));
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
                var x = margins.l + width *(data.data[i].pos - data.region.start) / (data.region.stop - data.region.start)
                var y = margins.t + height * (1-(Math.min(data.data[i][data.function], yMax) - yMin) / (yMax-yMin));
                if (x < 0 || y === undefined)
                    continue
                ctx.fillRect(x,y,1, margins.t + height - y );
            }
            ctx.closePath();

            // Reset context values
            ctx.strokeStyle = "#000000"
            ctx.fillStyle = "#000000"
            ctx.globalAlpha = 1.0;
        }

    }]);
})();
