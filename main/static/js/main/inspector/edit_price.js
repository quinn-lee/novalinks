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
    var nord_code = queryData["nord_code"];
    var sku_code = queryData["sku_code"];
    var price = queryData["price"];

    if (!nord_code || nord_code == undefined) {
        location.href = "/inspector/users/index.html";
    }
    if (!sku_code || sku_code == undefined) {
        location.href = "/inspector/users/index.html";
    }

    $("#sku_code_show").html(sku_code);
    $("#nord_code").val(nord_code)
    $("#sku_code").val(sku_code)
    $("#price").val(price)

    $("#price").focus(function(){
        $("#notice").hide();
    });
    $("#edit_price").submit(function(e){
        e.preventDefault();
        price = $("#price").val()
        if (!price) {
            $("#notice").html("请填写价格！");
            $("#notice").show();
            return;
        }
        var formData = new FormData();
        formData.append("nord_code", $("#nord_code").val());
        formData.append("sku_code", $("#sku_code").val());
        formData.append("price", price);

        $.ajax({
            url:"/api/v1.0/users/update_sku_price",
            type:"post",
            processData : false,// 必须要加这一句，否则会对formdata二次处理
            data: formData,
            contentType: false,
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (data) {
                if (data.errno == "0") {
                    // 修改成功，跳转到列表页
                    location.href = "/inspector/users/wms_inventories.html?nord_code="+nord_code;
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