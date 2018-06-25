(function() {
    angular.module("App")
    .directive("arrowSelect", [function () {
        return {
            restrict: "A",
            scope: { selection: "=",
                     items: "=",
                     target: "=",
                    },
            link: function(scope, element) {
                element.bind("keydown keypress", function (event) {
                    if (event.which === 38 || event.which === 40) {
                        event.preventDefault();

                        switch (event.which) {
                            case 38: scope.selection -= 1; break;
                            case 40: scope.selection += 1; break;
                        }

                        if (scope.selection < 0)
                            scope.selection = scope.items.length-1;
                        if (scope.selection >= scope.items.length)
                            scope.selection = 0;

                        scope.target = scope.items[scope.selection];
                        scope.$apply();
                    }
                });
            }
        };
    }]);
})();
