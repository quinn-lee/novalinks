function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {

    $.get("/api/v1.0/authorizations/unauthorized_users", function (resp) {
        if (resp.errno == "0") {
            var emails = resp.data;
            $( "#email" ).html(
				$( "#userTemplate" ).render( emails )
			);

        } else if ("4101" == resp.errno) {
            // 用户未登录
            location.href = "/login.html";
        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $("#email").focus(function(){
        $("#notice").hide();
    });
    $("#authorization_request").submit(function(e){
        e.preventDefault();
        email = $("#email").val();
        if (!email) {
            $("#notice").html("请选择卖家！");
            $("#notice").show();
            return;
        }
        // 将表单的数据存放到对象data中
        var data = {
            email: email
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/authorizations/request",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    // 创建成功，跳转到列表页
                    location.href = "/inspector/authorization/index1.html";
                }
                else {
                    // 其他错误信息，在页面中展示
                    $("#notice").html(data.errmsg);
                    $("#notice").show();
                }
            }
        });
    });

})