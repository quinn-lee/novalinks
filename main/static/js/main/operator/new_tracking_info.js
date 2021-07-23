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
                $("#waybill_id").val(resp.data['id'])
            }
            else {
                location.href = "/operator/waybill/waybills.html"
            }
        }
    });

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
         timepicker:true,
         format:'Y/m/d H:i'
    });
    $("#event_time").focus(function(){
        $("#notice").hide();
    });
    $("#location").focus(function(){
        $("#notice").hide();
    });
    $("#event").focus(function(){
        $("#notice").hide();
    });

    $("#create_tracking_info").submit(function(e){
        e.preventDefault();
        event_time = $("#event_time").val();
        loc = $("#location").val();
        event = $("#event").val();
        description = $("#description").val();
        if (!event_time) {
            $("#notice").html("请选择时间！");
            $("#notice").show();
            return;
        }
        if (!loc) {
            $("#notice").html("请填写地点！");
            $("#notice").show();
            return;
        }
        if (!event) {
            $("#notice").html("请填写事件！");
            $("#notice").show();
            return;
        }

        var formData = new FormData();
        formData.append("event_time", event_time);
        formData.append("location", loc);
        formData.append("event", event);
        formData.append("description", description);
        formData.append("id", $("#waybill_id").val())

        $.ajax({
            url:"/api/v1.0/waybills/tracking_info/create",
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