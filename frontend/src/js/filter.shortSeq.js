(function() {
    angular.module("App")
    .filter('shortSeq', function() {
        return function(input, len = 12) {
            var tail = Math.floor((len-5)/2)
            if (input.length >= len) {
                return input.substr(0,tail) + "[...]" + input.substr(input.length-tail,input.length);
            }
            return input;
        };
    });
})();
