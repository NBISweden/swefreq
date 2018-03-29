(function() {
  $.getJSON( "/api/schema?url=" + $(location).attr('href'), function(data) {
    $("#ldJsonTarget").html( JSON.stringify(data, null, 2) );
  });
})();