function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/message", function (resp) {
        if (resp.errno == "0") {
            var data = resp.data;
            $( "#messageShow" ).html(
				$( "#messageTemplate" ).render( data )
			);

        } else {
            
        }

    }, "json");

})