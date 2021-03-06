function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 页面初始化
function init_page() {
    var nowDate = new Date()
    var startDate = new Date()
    startDate.setDate(startDate.getDate() - 90)
    $("#start_date").val(startDate.getFullYear()+'/'+(parseInt(startDate.getMonth())+1)+'/'+startDate.getDate())
	$("#end_date").val(nowDate.getFullYear()+'/'+(parseInt(nowDate.getMonth())+1)+'/'+nowDate.getDate())
	var data = {
        start_date: $("#start_date").val(),
        end_date: $("#end_date").val(),
        action: 'search'
    };
    // 将data转为json字符串
    var jsonData = JSON.stringify(data);
    $.ajax({
        url:"/api/v1.0/orders/statistics",
        type:"post",
        data: jsonData,
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                var res = resp.data;
                $( "#table-tr" ).html(
                    $( "#trTemplate" ).render( res )
                );
                if (typeof(resultTable) == "undefined") {
                    resultTable = $('#result-listing').DataTable({
                        searching: false, paging: false, info: false
                    });
                }
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
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

    // 页面初始化
    init_page();

    $.get("/api/v1.0/users", function (resp) {
        if (resp.errno == "0") {
            var emails = resp.data;
            $( "#email" ).html(
				$( "#userTemplate" ).render( emails )
			);

        } else {
            alert(resp.errmsg);
        }

    }, "json");

    // 搜索提交事件
	$("#search-form").submit(function(e){
		e.preventDefault();
        if(!$("#start_date").val() || !$("#end_date").val()){
            $("#notice").html("统计必须输入起止时间！");
            $("#notice").show();
            return;
        };
        sd = new Date($("#start_date").val().replace(/-/,"/"));
        ed = new Date($("#end_date").val().replace(/-/,"/"));
        days = Math.floor((ed - sd) / (24 * 3600 * 1000));
        if(days > 366){
            $("#notice").html("时间间隔不能超过1年！");
            $("#notice").show();
            return;
        }
        $("#notice").hide();
		var data = {
            start_date: $("#start_date").val(),
            end_date: $("#end_date").val(),
            email: $("#email").val(),
            action: 'search'
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
		$.ajax({
            url:"/api/v1.0/orders/statistics",
            type:"post",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    var res = resp.data;
            		$( "#table-tr" ).html(
						$( "#trTemplate" ).render( res )
					);
                    if (typeof(resultTable) == "undefined") {
                        resultTable = $('#result-listing').DataTable({
                            searching: false, paging: false, info: false
                        });
                    }
                }
                else {
                    alert(resp.errmsg);
                }
            }
        });
	})

})