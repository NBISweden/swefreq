(function() {
    angular.module("App")
    .filter('formatVariant', function() {
        function shortenSeq(input, len=12) {
            var tail = Math.floor((len-5)/2)
            if (input.length >= len) {
                return input.substr(0,tail) + "[...]" + input.substr(input.length-tail,input.length);
            }
            return input;
        }

        return function(variant, len = 12) {
            var segments = variant['variantId'].split("-");
            var text = "";
            text += segments[0] + '-' + segments[1];
            text += ' ' + shortenSeq(segments[2], len);
            text += ' → ';
            text += ' ' + shortenSeq(segments[3], len);
            if ( variant['rsid'] ) {
                text += " (" + variant['rsid'] + ")";
            }
            return text;
        };
    });
})();
