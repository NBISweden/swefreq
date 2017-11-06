(function() {
    angular.module("App")
    .directive("consent", ["$cookies", function ($cookies) {
        return {
            scope: {},
            template:
                "<div style=\"position: relative; z-index: 1000\">" +
                "<div style=\"background: #eee; position: fixed; bottom: 0; left: 0; right: 0; height: 20px\" ng-hide=\"consent()\">" +
                "<span style=\"margin-left: 5px;\">This site uses cookies, please see our <a href=\"https://swefreq.nbis.se/#/privacyPolicy/\">privacy policy</a>, ok, I <a href=\"\" ng-click=\"consent(true)\">agree.</a></span>" +
                "<span style=\"float: right;margin-right: 5px;\"><a href=\"\" ng-click=\"consent(true)\">X</a></span>" +
                "</div>" +
                "</div>",
            controller: function ($scope) {
                var _consent = $cookies.get("consent");
                $scope.consent = function (consent) {
                    if (consent === undefined) {
                        return _consent;
                    } else if (consent) {
                        $cookies.put("consent", true);
                        _consent = true;
                    }
                };
            }
        };
    }]);
})();
