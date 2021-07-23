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
    var id = queryData["id"];

    $.ajax({
        url:"/api/v1.0/waybills/edit?id="+id,
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                $("#w_no_show").html(resp.data['w_no']);
                $("#waybill_id").val(resp.data['id']);

            }
            else {
                location.href = "/operator/waybill/waybills.html"
            }
        }
    });

    $("#click_upload").click(function(){
        $("#notice").hide();
    });

    $("#upload_lading_bill").submit(function(e){
        e.preventDefault();
        lading_bill = $("#lading_bill")[0].files[0]
        if (!lading_bill) {
            $("#notice").html("请选择文件上传！");
            $("#notice").show();
            return;
        }
        var formData = new FormData();
        formData.append("lading_bill",lading_bill);
        formData.append("id", $("#waybill_id").val())

        $.ajax({
            url:"/api/v1.0/waybills/upload_lading_bill",
            type:"post",
            processData : false,// 必须要加这一句，否则会对formdata二次处理
            data: formData,
            contentType: false,
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    // 创建成功，跳转到列表页
                    location.href = "/operator/waybill/waybills.html";
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