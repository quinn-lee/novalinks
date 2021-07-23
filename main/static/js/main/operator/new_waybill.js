function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(document).ready(function() {

    $.datetimepicker.setLocale('ch');
    $('.datepicker').datetimepicker({
        i18n:{
          ch:{
           months:[
            '一月','二月','三月','四月',
            '五月','六月','七月','八月',
            '九月','十月','十一月','十二月',
           ],
           dayOfWeek:[
            "日", "一", "二", "三", "四", "五", "六",
           ]
          }
         },
         timepicker:false,
         format:'Y/m/d'
    });

    $.get("/api/v1.0/authorizations/authorized", function (resp) {
        if (resp.errno == "0") {
            var sellers = resp.data;
            $( "#seller" ).html(
				$( "#sellerTemplate" ).render( sellers )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    $.get("/api/v1.0/depots/index", function (resp) {
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

        var formData = new FormData();
        formData.append("lading_bill",$("#lading_bill")[0].files[0]);
        formData.append("w_no", w_no);
        formData.append("seller_email", seller);
        formData.append("depot_id", depot);
        formData.append("billing_weight", $("#billing_weight").val());
        formData.append("customs_apply", $("#customs_apply").find("option:selected").val());
        formData.append("delivery_time", $("#delivery_time").val());
        formData.append("customs_declaration", $("#customs_declaration").find("option:selected").val());
        formData.append("etd", $("#etd").val());
        formData.append("eta", $("#eta").val());

        $.ajax({
            url:"/api/v1.0/waybills/create",
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