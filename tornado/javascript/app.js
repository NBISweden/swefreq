(function() {
    // create the module and name it App
    var App = angular.module('App', ['ngRoute'])
    var gData = {'userName':'',
		 'email':'',
		 'affiliation':'',
		 'trusted':false,
		 'admin':false}

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('mainController', function($http, $scope) {
	var localThis = this;
	localThis.data = gData;
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('sweFreqController', function($http, $scope) {
	var localThis = this;
	this.userName = '';
	this.email = '';
	localThis.data = gData;

	this.getUsers = function(){
	    $http.get('/getUser').success(function(data){
		console.log(data);
		localThis.data.userName = data.user;
		localThis.data.email = data.email;
		localThis.data.trusted = data.trusted;
		localThis.data.isInDatabase = data.isInDatabase;
		localThis.data.admin = data.admin;
		if(data.admin == true){
		    $http.get('/getOutsandingRequests').success(function(data){
			localThis.data.requests = data;
		    });
		    $http.get('/getApprovedUsers').success(function(data){
			localThis.data.approvedUsers = data;
		    });
		};
	    });
	};
	this.getUsers();

	this.denyUser = function(userData){
	    $http.get('/denyUser/' + userData.email).success(function(data){
		localThis.getUsers();
	    });
	};

	this.deleteUser = function(userData){
	    $http.get('/deleteUser/' + userData.email).success(function(data){
		localThis.getUsers();
	    });
	};

	this.approvedUser = function(userData){
	    $http.get('/approveUser/' + userData.email).success(function(data){
		$http.get('/getOutsandingRequests').success(function(data){
		    localThis.getUsers();
		});
	    });
	};
    });

     /////////////////////////////////////////////////////////////////////////////////////

    App.controller('dataBeaconController', function($http, $scope) {
	var localThis = this;
        this.search = function() {
            $http.get('query', { 'params': { 'chrom': this.data.chromosome, 'pos': this.data.position, 'allele': this.data.allele, 'dataset': this.data.dataset}})
                .then(function (response){
                    if (response.data['response']['exists']) {
                        localThis.response = "This allele exists in the dataset"
                    }
                    else {
                        localThis.response = "Sorry, can't find it"
                    }
                },
                function (response){
                    localThis.response="ERROR";
                });
        }
    });

     /////////////////////////////////////////////////////////////////////////////////////

    App.controller('downloadDataController', function($http, $scope) {
	this.lChecked = true;
	var localThis = this;
	localThis.data = gData;
	this.isChecked = function(){
	    if(localThis.lChecked){
		$http.get('/logEvent/consent').success(function(data){
		    console.log('Consented');
		});
	    }
	    localThis.lChecked = false;
	    localThis.checked = true;
	};

	this.downloadData = function(){
	    $http.get('/logEvent/download').success(function(data){
		console.log("Downloading")
	    });
	};
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('exacBrowserController', function($http, $scope) {
	var localThis = this;
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('requestController', function($http, $scope, $location) {
	var localThis = this;
	localThis.data = gData;

	this.sendRequest = function(locations){
	    $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
	    $http({url:'/requestAccess',
		   method:'POST',
		   data:$.param({'email':localThis.data.email,
				 'userName':localThis.data.userName,
				 'affiliation':localThis.data.affiliation})
		  })
		.success(function(data){
		    console.log(data);
		    $location.path("/addedRequest");
		});
	};
    });

    /////////////////////////////////////////////////////////////////////////////////////

    App.controller('addedRequestController', function($http, $scope) {
	var localThis = this;
    });

    ////////////////////////////////////////////////////////////////////////////
    // configure routes
    App.config(function($routeProvider) {
	$routeProvider
	// Read only view
	    .when('/', {
		templateUrl : 'static/home.html'
	    })
	// Data beacon
	    .when('/dataBeacon/', {
		templateUrl : 'static/dataBeacon.html'
	    })
	// Data Download
	    .when('/downloadData/', {
		templateUrl : 'static/downloadData.html'
	    })
	// Request Access
	    .when('/requestAccess/', {
		templateUrl : 'static/requestAccess.html'
	    })
	// Request Access Sent
	    .when('/addedRequest/', {
		templateUrl : 'static/addedRequest.html'
	    })
	// ExAC Browser
	    .when('/exacBrowser/', {
		templateUrl : 'static/exacBrowser.html'
	    })
    });
})();

