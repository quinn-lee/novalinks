function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/authorizations/pending_requests", function(resp){
        if ("4101" == resp.errno) {
            // 用户未登录
            location.href = "/login.html";
        } else {
        	if (resp.data.length > 0 ){
        	    $("#requests").html(resp.data.length + "个");
                $("#noti").show();
                $('#noti-content').css('display','');
        	}
        }
    });

})