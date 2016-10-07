indexHead="""
<!DOCTYPE html>
<!-- define angular app -->
<html ng-app="App">
  <head>
    <!-- SCROLLS -->
    <meta charset="utf-8" />
    <!-- Bootstrap -->
    <link rel="stylesheet"
          href="//netdna.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css" />
    <link rel="stylesheet"
          href="//netdna.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.css" />
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js">
    </script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.min.js">
    </script>
    <!-- Angular -->
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.0/angular.min.js">
    </script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.0/angular-route.min.js">
    </script>
    <!-- Angular grid gui -->
    <link rel="stylesheet"
          href="/javascript/main.css"
          type="text/css" />
    <link rel="stylesheet"
          href="/javascript/local.css"
          type="text/css" />
    <!-- The application -->
    <script src="javascript/app.js"></script>
  </head>
"""
indexHtml="""
  <!-- define angular controller -->
  <body ng-controller="mainController as mainCtrl">
    <nav class="navbar navbar-default">
      <div class="container">
        <a class="navbar-brand pull-left"
           href="/#/">SweFreq</a>
        <ul class="nav navbar-nav navbar-right">
        <a href="/#/dataBeacon/"
           role="button"
           class="btn btn-default">Data Beacon</a>
        <a href="{{ExAC}}"
           role="button"
           class="btn btn-default">ExAC Browser</a>
        <a href="/#/downloadData/"
           role="button"
           class="btn btn-default">Download Data</a>&#160; &#160; 
        <div class="btn-group navbar-btn">{%if user_name != None%}
        {{user_name}} 
        <a href="/logout">Logout</a>
        <br />{{email}} {% else %} 
        <br />
        <a href="/login">Login</a>{% end %}</div></ul>
      </div>
    </nav>
    <div id="main">
      <!-- angular templating -->
      <!-- this is where content will be injected by angular -->
      <div ng-view=""></div>
    </div>
      </div>
    <footer class="text-center">
    <div class="col-sm-12 col-md-12 col-lg-7 col-lg-offset-2 logo-div">
        <a href="https://nbis.se"><img class="logo" src="javascript/nbislogo-green-r.png" alt="NBIS"></a>
        <a href="https://www.scilifelab.se"><img class="logo scilife" src="javascript/SLL_logo-r.png" alt="SciLifeLab"></a>
    </div>
    </footer>
  </body>
</html>
"""
notAuthorizedHtml="""
  <!-- define angular controller -->
  <body ng-controller="mainController as mainCtrl">
    <nav class="navbar navbar-default">
      <div class="container">
        <a class="navbar-brand pull-left"
           href="/#/">SweFreq</a>
        <ul class="nav navbar-nav navbar-right">
        <a href="/#/dataBeacon/"
           role="button"
           class="btn btn-default">Data Beacon</a>
        <a href="{{ExAC}}"
           role="button"
           class="btn btn-default">ExAC Browser</a>&#160; &#160; 
        <div class="btn-group navbar-btn">
          <br />
          <a href="/login">Login</a>
        </div></ul>
      </div>
    </nav>
    <div id="main">
      <!-- angular templating -->
      <!-- this is where content will be injected -->
      <div ng-view=""></div>
    </div>
    <footer class="text-center">
    <div class="col-sm-12 col-md-12 col-lg-7 col-lg-offset-2 logo-div">
        <a href="https://nbis.se"><img class="logo" src="javascript/nbislogo-green-r.png" alt="NBIS"></a>
        <a href="https://www.scilifelab.se"><img class="logo scilife" src="javascript/SLL_logo-r.png" alt="SciLifeLab"></a>
    </div>
    </footer>
  </body>
</html>
"""
indexNoAccess="""
  <!-- define angular controller -->
  <body ng-controller="mainController as mainCtrl">
    <nav class="navbar navbar-default">
      <div class="container">
        <a class="navbar-brand pull-left"
           href="/#/">SweFreq</a>
        <ul class="nav navbar-nav navbar-right">
        <a href="/#/requestAccess/"
           role="button"
           class="btn btn-default">Request Access</a>&#160; &#160; 
        <div class="btn-group navbar-btn">{%if user_name != None%}
        {{user_name}} 
        <a href="/logout">Logout</a>
        <br />{{email}} {% else %} 
        <br />
        <a href="/login">Login</a>{% end %}</div></ul>
      </div>
    </nav>
    <div id="main">
      <!-- angular templating -->
      <!-- this is where content will be injected by angular -->
      <div ng-view=""></div>
    </div>
    <footer class="text-center">
    <div class="col-sm-12 col-md-12 col-lg-7 col-lg-offset-2 logo-div">
        <a href="https://nbis.se"><img class="logo" src="javascript/nbislogo-green-r.png" alt="NBIS"></a>
        <a href="https://www.scilifelab.se"><img class="logo scilife" src="javascript/SLL_logo-r.png" alt="SciLifeLab"></a>
    </div>
    </footer>
  </body>
</html>
"""
