function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#email").focus(function(){
        $("#login-err").hide();
    });
    $("#password").focus(function(){
        $("#login-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        email = $("#email").val();
        passwd = $("#password").val();
        if (!email) {
            $("#login-err").html("请填写正确的邮箱！");
            $("#login-err").show();
            return;
        } 
        if (!passwd) {
            $("#login-err").html("请填写密码!");
            $("#login-err").show();
            return;
        }
        // 将表单的数据存放到对象data中
        var data = {
            email: email,
            password: passwd
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/sessions",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    if ( data.data == "admin" ) {
                        // admin登录成功，跳转到主页
                        location.href = "/admin/users/index.html";
                    } else if ( data.data == "operator" ) {
                        // operator登录成功，跳转到主页
                        location.href = "/operator/authorization/index.html";
                    } else if ( data.data == "seller" ) {
                        // seller登录成功，跳转到主页
                        location.href = "/seller/authorization/index.html";
                    }
                }
                else {
                    // 其他错误信息，在页面中展示
                    $("#login-err").html(data.errmsg);
                    $("#login-err").show();
                }
            }
        });
    });
})