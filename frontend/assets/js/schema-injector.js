/*
 *  This function could not be included in angular, due to what we believe is
 *  a timing issue. When we had angular inject the schema.org annotation, it
 *  simply would not register in the testing tool - so now we inject it before
 *  loading the angular app.
 *
 *  The function passes the current url to the backend, which uses it to
 *  the correct schema.org annotation from the database.
 */
(function() {
  $.getJSON( "/api/schema?url=" + $(location).attr("href"), function(data) {
    $("#ldJsonTarget").html( JSON.stringify(data, null, 2) );
  });
})();