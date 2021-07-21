function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 页面初始化
function init_page() {
    $.ajax({
        url:"/api/v1.0/pending_seller_authorization_requests",
        type:"get",
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
            } else if ("4101" == resp.errno) {
                // 用户未登录
                location.href = "/login.html";
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
}

function auth(obj) {
    $.ajax({
        url:"/api/v1.0/processing_auth?id="+obj.id+"&status=1",
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                location.href = "/seller/authorization/index.html";
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
}

function unauth(obj) {
    $.ajax({
        url:"/api/v1.0/processing_auth?id="+obj.id+"&status=2",
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                location.href = "/seller/authorization/index.html";
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

})