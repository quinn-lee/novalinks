function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 页面初始化
function init_page() {
    var data = {
        email: "",
        role: ""
    };
    // 将data转为json字符串
    var jsonData = JSON.stringify(data);
    $.ajax({
        url:"/api/v1.0/users/index",
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
    // 页面初始化
    init_page();
    // 搜索提交事件
	$("#search-form").submit(function(e){
		e.preventDefault();
		var data = {
            email: $("#email").val(),
            role: $("#role").val()
        };
        // 将data转为json字符串
        var jsonData = JSON.stringify(data);
		$.ajax({
            url:"/api/v1.0/users/index",
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