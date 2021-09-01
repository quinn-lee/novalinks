function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function() {

    var queryData = decodeQuery();
    var role = queryData["role"];
    var email = queryData["email"];
    var name = queryData["name"];
    var status = queryData["status"];
    var nord_code = queryData["nord_code"];

    $("#role").val(role)
    $("#email").val(email)
    $("#name").val(name)
    $("#nord_code").val(nord_code)
    $("#status").val(status)

    $("#role").focus(function(){
        $("#notice").hide();
    });
    $("#email").focus(function(){
        $("#notice").hide();
    });
    $("#name").focus(function(){
        $("#notice").hide();
    });
    $("#password").focus(function(){
        $("#notice").hide();
    });
    $("#password_confirm").focus(function(){
        $("#notice").hide();
    });
    $("#status").focus(function(){
        $("#notice").hide();
    });
    $("#edit_user").submit(function(e){
        e.preventDefault();
        role = $("#role").val();
        email = $("#email").val();
        name = $("#name").val();
        password = $("#password").val();
        password_confirm = $("#password_confirm").val();
        nord_code = $("#nord_code").val();
        status = $("#status").val();
        if (!role) {
            $("#notice").html("请选择角色！");
            $("#notice").show();
            return;
        }
        if (!email) {
            $("#notice").html("请填写正确的邮箱！");
            $("#notice").show();
            return;
        }
        if (!name) {
            $("#notice").html("请填写名称！");
            $("#notice").show();
            return;
        }
        if (!status) {
            $("#notice").html("请选择状态！");
            $("#notice").show();
            return;
        }
        if (password != password_confirm) {
            $("#notice").html("密码与密码确认必须相同!");
            $("#notice").show();
            return;
        }
        // 将表单的数据存放到对象data中
        var data = {
            role: role,
            email: email,
            name: name,
            password: password,
            password_confirm: password_confirm,
            nord_code: nord_code,
            status: status
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/users/update",
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
                    location.href = "/admin/users/index.html";
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