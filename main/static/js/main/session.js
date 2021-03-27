function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/session", function(resp){
        if ("4101" == resp.errno) {
            // 用户未登录
            location.href = "/login.html";
        } else {
        	$("#login-name").html(resp.data['name']);
        }
    });

    $("#logout a").click(function(e){
    	$.ajax({
            url:"/api/v1.0/session",
            type:"delete",
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    location.href = "/login.html";
                }
                else {
                	location.href = "/login.html";
                }
            }
        });
    })

})