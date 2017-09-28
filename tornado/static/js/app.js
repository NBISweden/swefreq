(function() {

    /////////////////////////////////////////////////////////////////////////////////////
    // create the module and name it App
    var App = angular.module('App', ['ngRoute', 'ngCookies'])
    var gData = {'userName':'',
                 'email':'',
                 'affiliation':'',
                 'trusted':false,
                 'admin':false}


    App.factory('User', function($http) {
        return function() {
            return $http.get('/api/users/me');
        };
    });


    App.factory('DatasetUsers', function($http, $cookies, $q) {
        var service = {};
        $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";

        service.getUsers = function(dataset) {
            var defer = $q.defer();
            var data = {'pending': [], 'current': []};
            $q.all([
                $http.get( '/api/datasets/' + dataset + '/users_pending' ).then(function(d) {
                    data['pending'] = d.data.data;
                }),
                $http.get( '/api/datasets/' + dataset + '/users_current' ).then(function(d) {
                    data['current'] = d.data.data;
                })
            ]).then(function(d) {
                defer.resolve(data);
            });
            return defer.promise;
        };

        service.approveUser = function(dataset, email) {
            return $http.post(
                    '/api/datasets/' + dataset + '/users/' + email + '/approve',
                    $.param({'_xsrf': $cookies.get('_xsrf')})
                )
        };

        service.revokeUser = function(dataset, email) {
            return $http.post(
                    '/api/datasets/' + dataset + '/users/' + email + '/revoke',
                    $.param({'_xsrf': $cookies.get('_xsrf')})
                )
        };

        service.requestAccess = function(dataset, user) {
            return $http({url:'/api/datasets/' + dataset + '/users/' + user.email + '/request',
                   method:'POST',
                   data:$.param({
                           'email':       user.email,
                           'userName':    user.userName,
                           'affiliation': user.affiliation,
                           'country':     user.country['name'],
                           '_xsrf':       $cookies.get('_xsrf'),
                           'newsletter':  user.newsletter ? 1 : 0
                        })
                });
        };

        return service;
    });

    App.factory('Log', function($http, $cookies) {
        var service = {};
        $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";

        service.consent = function(dataset) {
            return $http.post('/api/datasets/' + dataset + '/log/consent',
                    $.param({'_xsrf': $cookies.get('_xsrf')})
                );
        };
        service.download = function(dataset) {
            return $http.post(
                    '/api/datasets/' + dataset + '/log/download',
                    $.param({'_xsrf': $cookies.get('_xsrf')})
                );
        };

        return service;
    });


    App.factory('Dataset', function($http, $q, $location, $sce) {
        var state = {dataset: null};
        return function() {
            var defer = $q.defer();

            var path = $location.path().split('/');
            var dataset = path[2];
            if ( path[1] != 'dataset' ) {
                state = "Some strange error 2";
                defer.reject("Some strange error 1");
            }
            else {
                $q.all([
                    $http.get('/api/datasets/' + dataset).then(function(data){
                        var d = data.data;
                        d.version.description = $sce.trustAsHtml( d.version.description );
                        d.version.terms       = $sce.trustAsHtml( d.version.terms );
                        state['dataset'] = d;
                    }),
                    $http.get('/api/datasets/' + dataset + '/collection').then(function(data){
                        state.collections = data.data.collections;
                        state.study = data.data.study;

                        console.log(state.collections);

                        cn = state.study.contact_name;
                        state.study.contact_name_uc = cn.charAt(0).toUpperCase() + cn.slice(1);
                    })
                ]).then(function(data) {
                    defer.resolve(state);
                });
            }
            return defer.promise;
        }
    });

    App.factory('Beacon', function($http, $q) {
        var service = {};

        function _getBeaconReferences(name) {
            var references = [];
            for (var i = 0; i<service.data['datasets'].length; i++) {
                dataset = service.data['datasets'][i];
                if ( dataset['id'] == name ) {
                    references.push(dataset['reference']);
                }
            }
            return references;
        }

        service.getBeaconReferences = function(name) {
            var defer = $q.defer();
            if ( service.hasOwnProperty('id') ) {
                defer.resolve( _getBeaconReferences(name) );
            }
            else {
                $http.get('/api/beacon/info').success(function(data) {
                    service.data = data;
                    defer.resolve(_getBeaconReferences(name));
                });
            }
            return defer.promise
        };

        service.queryBeacon = function(query) {
            return $http.get('/api/beacon/query', {
                    'params': {
                        'chrom':           query.chromosome,
                        'pos':             query.position - 1, // Beacon is 0-based
                        'allele':          query.allele,
                        'referenceAllele': query.referenceAllele,
                        'dataset':         query.dataset.short_name,
                        'ref':             query.reference
                    }
                });
        };

        return service;
    });


    /////////////////////////////////////////////////////////////////////////////////////
    App.directive('consent', function ($cookies) {
        return {
            scope: {},
            template:
                '<div style="position: relative; z-index: 1000">' +
                '<div style="background: #eee; position: fixed; bottom: 0; left: 0; right: 0; height: 20px" ng-hide="consent()">' +
                '<span style="margin-left: 5px;">This site uses cookies, please see our <a href="https://swefreq.nbis.se/#/privacyPolicy/">privacy policy</a>, ok, I <a href="" ng-click="consent(true)">agree.</a></span>' +
                '<span style="float: right;margin-right: 5px;"><a href="" ng-click="consent(true)">X</a></span>' +
                '</div>' +
                '</div>',
            controller: function ($scope) {
                var _consent = $cookies.get('consent');
                $scope.consent = function (consent) {
                    if (consent === undefined) {
                        return _consent;
                    } else if (consent) {
                        $cookies.put('consent', true);
                        _consent = true;
                    }
                };
            }
        };
    });

    App.directive('myDatasetHeader', function() {
        return {
            restrict: 'E',
            templateUrl: 'static/js/ng-templates/dataset-header.html',
            link: function(scope, element, attrs) {
                scope.name = function() {
                    return attrs.dataset;
                };
            },
        };
    });

    App.directive('myNavbar', ['Dataset', function(Dataset) {
        return {
            restrict: 'E',
            templateUrl: 'static/js/ng-templates/dataset-navbar.html',
            link: function(scope, element, attrs) {
                scope.createUrl = function(subpage) {
                    return '/dataset/' + scope.dataset + '/' + subpage;
                };
                scope.isActive = function(tab) {
                    if ( tab == attrs.tab ) {
                        return 'active';
                    }
                    else {
                        return '';
                    }
                };
                scope.is_admin = false;
                Dataset().then(function(data){
                        scope.is_admin    = data.dataset.is_admin;
                        scope.dataset     = data.dataset.short_name;
                        scope.browser_uri = data.dataset.browser_uri;
                    }
                );
            },
        };
    }]);


    App.controller('mainController', function($location) {
        var localThis = this;
        localThis.url = function () { return $location.path() };
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('homeController', function($http, $sce) {
        var localThis = this;
        localThis.datasets = [];
        localThis.getDatasets = function(){
            $http.get('/api/datasets').success(function(res){
                var len = res.data.length;
                for (var i = 0; i < len; i++) {
                    d = res.data[i];
                    d.version.description = $sce.trustAsHtml(d.version.description)

                    localThis.datasets.push(d);
                }
            });
        };
        localThis.getDatasets();
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('datasetController', ['$http', '$routeParams', 'User', 'Dataset',
                                function($http, $routeParams, User, Dataset) {
        var localThis = this;
        var dataset = $routeParams["dataset"];

        User().then(function(data) {
            localThis.user = data.data;
        });

        Dataset().then(function(data){
            localThis.dataset = data.dataset;
            localThis.collections = data.collections;
            localThis.study = data.study;
        });
    }]);

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('datasetDownloadController', ['$http', '$routeParams', 'User', 'Dataset', 'DatasetUsers', 'Log',
                                function($http, $routeParams, User, Dataset, DatasetUsers, Log) {
        var localThis = this;
        var dataset = $routeParams["dataset"];
        localThis.authorization_level = 'loggedout';

        $http.get('/api/countries').success(function(data) {
            localThis.availableCountries = data['countries'];
        });

        User().then(function(data) {
            localThis.user = data.data;
            updateAuthorizationLevel();
        });

        Dataset().then(function(data){
            localThis.dataset = data.dataset;
            updateAuthorizationLevel();
        });

        $http.get('/api/datasets/' + dataset + '/files').success(function(data){
            localThis.files = data.files;
        });

        function updateAuthorizationLevel () {
            if (!localThis.hasOwnProperty('user') || localThis.user.user == null) {
                localThis.authorization_level = 'loggedout';
            }
            else if (localThis.hasOwnProperty('dataset')) {
                localThis.authorization_level = localThis.dataset.authorization_level;
            }
        };

        localThis.sendRequest = function(valid){
            if (!valid) {
                return;
            }
            DatasetUsers.requestAccess(
                    dataset, localThis.user
                ).success(function(data){
                    localThis.authorization_level = 'thank-you';
                });
        };

        has_already_logged = false;
        localThis.consented = function(){
            if (!has_already_logged){
                has_already_logged = true;
                Log.consent(dataset);
            }
        };

        localThis.downloadData = function(){
            Log.download(dataset);
        };
    }]);

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('datasetAdminController', ['$http', '$routeParams', 'User', 'Dataset', 'DatasetUsers',
                                function($http, $routeParams, User, Dataset, DatasetUsers) {
        var localThis = this;
        var dataset = $routeParams["dataset"];

        getUsers();
        function getUsers() {
            DatasetUsers.getUsers( dataset ).then( function(data) {
                localThis.users = data;
            });
        }

        User().then(function(data) {
            localThis.user = data.data;
        });

        Dataset().then(function(data){
            localThis.dataset = data.dataset;
        });

        localThis.revokeUser = function(userData) {
            DatasetUsers.revokeUser(
                    dataset, userData.email
                ).success(function(data){
                    getUsers();
                });
        };

        localThis.approveUser = function(userData){
            DatasetUsers.approveUser(
                    dataset, userData.email
                ).success(function(data) {
                    getUsers();
                });
        };
    }]);

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('datasetBeaconController', ['$http', '$routeParams', 'Beacon', 'Dataset', 'User',
                                function($http, $routeParams, Beacon, Dataset, User) {
        var localThis = this;
        var dataset = $routeParams["dataset"];
        localThis.queryResponses = [];

        Beacon.getBeaconReferences(dataset).then(
                function(data) {
                    localThis.references = data;
                }
            );

        User().then(function(data) {
            localThis.user = data.data;
        });

        Dataset().then(function(data){
            localThis.dataset = data.dataset;
        });

        localThis.search = function() {
            Beacon.queryBeacon(localThis).then(function (response) {
                    d = response.data;
                    d.query.position += 1; // Beacon is 0-based
                    d.response.state = d.response.exists ? 'Present' : 'Absent';
                    localThis.queryResponses.push(d);
                },
                function (response){
                    localThis.queryResponses.push({
                        'response': { 'state': 'Error' },
                        'query': {
                            'chromosome':      localThis.chromosome,
                            'position':        localThis.position,
                            'allele':          localThis.allele,
                            'referenceAllele': localThis.referenceAllele,
                            'reference':       localThis.reference
                        }
                    });
                });
        };
    }]);

    ////////////////////////////////////////////////////////////////////////////
    // configure routes
    App.config(function($routeProvider, $locationProvider) {
        $routeProvider
            .when('/',                                  { templateUrl: 'static/js/ng-templates/home.html'             })
            .when('/dataBeacon/',                       { templateUrl: 'static/js/ng-templates/dataBeacon.html'       })
            .when('/dataset/:dataset',                  { templateUrl: 'static/js/ng-templates/dataset.html'          })
            .when('/dataset/:dataset/terms',            { templateUrl: 'static/js/ng-templates/dataset-terms.html'    })
            .when('/dataset/:dataset/download',         { templateUrl: 'static/js/ng-templates/dataset-download.html' })
            .when('/dataset/:dataset/beacon',           { templateUrl: 'static/js/ng-templates/dataset-beacon.html'   })
            .when('/dataset/:dataset/admin',            { templateUrl: 'static/js/ng-templates/dataset-admin.html'    })
            .otherwise(                                 { templateUrl: 'static/js/ng-templates/404.html'              });

        // Use the HTML5 History API
        $locationProvider.html5Mode(true);
    });
})();
