function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function() {

    $.get("/api/v1.0/query_authorized_users", function (resp) {
        if (resp.errno == "0") {
            var sellers = resp.data;
            $( "#seller" ).html(
				$( "#sellerTemplate" ).render( sellers )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $.get("/api/v1.0/query_depots", function (resp) {
        if (resp.errno == "0") {
            var sellers = resp.data;
            $( "#depot" ).html(
				$( "#depotTemplate" ).render( sellers )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $("#seller").focus(function(){
        $("#notice").hide();
    });
    $("#w_no").focus(function(){
        $("#notice").hide();
    });
    $("#depot").focus(function(){
        $("#notice").hide();
    });
    $("#new_waybill").submit(function(e){
        e.preventDefault();
        seller = $("#seller").val();
        w_no = $("#w_no").val();
        depot = $("#depot").val();
        if (!seller) {
            $("#notice").html("请选择卖家！");
            $("#notice").show();
            return;
        }
        if (!w_no) {
            $("#notice").html("请填写运单号！");
            $("#notice").show();
            return;
        }
        if (!depot) {
            $("#notice").html("请选择收件仓库！");
            $("#notice").show();
            return;
        }

        // 将表单的数据存放到对象data中
        var data = {
            w_no: w_no,
            seller_email: seller,
            depot_id: depot
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/waybill_create",
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
                    location.href = "/operator/waybill/new.html";
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