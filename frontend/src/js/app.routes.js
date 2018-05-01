(function() {
    ////////////////////////////////////////////////////////////////////////////
    // configure routes
    angular.module("App")
    .config(["$routeProvider", "$locationProvider", function($routeProvider, $locationProvider) {
        $routeProvider
            .when("/",                                                  { templateUrl: "static/templates/ng-templates/home.html"                })
            .when("/login",                                             { templateUrl: "static/templates/ng-templates/login.html"               })
            .when("/profile",                                           { templateUrl: "static/templates/ng-templates/profile.html"             })
            .when("/error",                                             { templateUrl: "static/templates/ng-templates/error.html"               })
            .when("/security_warning",                                  { templateUrl: "static/templates/ng-templates/security_warning.html"    })
            .when("/dataset/:dataset",                                  { templateUrl: "static/templates/ng-templates/dataset.html"             })
            .when("/dataset/:dataset/terms",                            { templateUrl: "static/templates/ng-templates/dataset-terms.html"       })
            .when("/dataset/:dataset/download",                         { templateUrl: "static/templates/ng-templates/dataset-download.html"    })
            .when("/dataset/:dataset/beacon",                           { templateUrl: "static/templates/ng-templates/dataset-beacon.html"      })
            .when("/dataset/:dataset/admin",                            { templateUrl: "static/templates/ng-templates/dataset-admin.html"       })
            .when("/dataset/:dataset/version/:version",                 { templateUrl: "static/templates/ng-templates/dataset.html"             })
            .when("/dataset/:dataset/version/:version/terms",           { templateUrl: "static/templates/ng-templates/dataset-terms.html"       })
            .when("/dataset/:dataset/version/:version/download",        { templateUrl: "static/templates/ng-templates/dataset-download.html"    })
            .when("/dataset/:dataset/version/:version/beacon",          { templateUrl: "static/templates/ng-templates/dataset-beacon.html"      })
            .when("/dataset/:dataset/browser",                          { templateUrl: "static/templates/ng-templates/dataset-browser.html"     })
            .when("/dataset/:dataset/browser/not_found",                { templateUrl: "static/templates/ng-templates/browser-not_found.html"   })
            .when("/dataset/:dataset/browser/gene/:gene",               { templateUrl: "static/templates/ng-templates/browser-gene.html"        })
            .when("/dataset/:dataset/browser/region/:region",           { templateUrl: "static/templates/ng-templates/browser-region.html"      })
            .when("/dataset/:dataset/browser/transcript/:transcript",   { templateUrl: "static/templates/ng-templates/browser-transcript.html"  })
            .when("/dataset/:dataset/browser/variant/:variant",         { templateUrl: "static/templates/ng-templates/browser-variant.html"     })
            .otherwise(                                                 { templateUrl: "static/templates/ng-templates/404.html"                 });

        // Use the HTML5 History API
        $locationProvider.html5Mode(true);
    }]);
})();
