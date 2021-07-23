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

function show_billing(obj) {
    $.ajax({
        url:"/api/v1.0/waybills/show_billing?id="+obj.id.split("_")[1],
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                open(resp.data);
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
}

function delete_billing(obj) {
    conf = confirm("确认要删除该运单吗？");
    if (conf == false) {
        return
    }
    $.ajax({
        url:"/api/v1.0/waybills/delete_billing?id="+obj.id.split("_")[1],
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                location.href = "/operator/waybill/waybills.html"
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
}

function delete_waybill(obj) {
    conf = confirm("确认要删除该运单吗？");
    if (conf == false) {
        return
    }
    $.ajax({
        url:"/api/v1.0/waybills/delete?id="+obj.id.split("_")[1],
        type:"get",
        contentType: "application/json",
        dataType: "json",
        headers:{
            "X-CSRFToken":getCookie("csrf_token")
        },
        success: function (resp) {
            if (resp.errno == "0") {
                location.href = "/operator/waybill/waybills.html"
            }
            else {
                alert(resp.errmsg);
            }
        }
    });
}

$(document).ready(function() {

    var queryData = decodeQuery();
    var w_no = queryData["w_no"];

    $("#w_no").val(w_no)


    //提示信息
    $.fn.dataTable.ext.errMode = 'none';

    var lang = {
        "sProcessing": "获取数据中...",
        "sLengthMenu": "每页 _MENU_ 条",
        "sZeroRecords": "没有匹配结果",
        "sInfo": "当前显示第 _START_ 至 _END_ 条，共 _TOTAL_ 条。",
        "sInfoEmpty": "当前显示第 0 至 0 条，共 0 条",
        "sInfoFiltered": "(由 _MAX_ 项结果过滤)",
        "sInfoPostFix": "",
        "sSearch": "搜索:",
        "sUrl": "",
        "sEmptyTable": "表中数据为空",
        "sLoadingRecords": "载入中...",
        "sInfoThousands": ",",
        "oPaginate": {
            "sFirst": "首页",
            "sPrevious": "上页",
            "sNext": "下页",
            "sLast": "末页",
            "sJump": "跳转"
        },
        "oAria": {
            "sSortAscending": ": 以升序排列此列",
            "sSortDescending": ": 以降序排列此列"
        }
    };

    //初始化表格
    table = $("#table_details")
        .on('error.dt', function (e, settings, techNote, message) {
            console.warn(message)
        }).dataTable({
            "aLengthMenu": [
                    [100, 500, 1000],
                    [100, 500, 1000] // change per page values here
                ],
            iDisplayLength: 100,
            language: lang, //提示信息
            autoWidth: false, //禁用自动调整列宽
            stripeClasses: ["odd", "even"], //为奇偶行加上样式，兼容不支持CSS伪类的场合
            processing: true, //隐藏加载提示,自行处理
            serverSide: true, //启用服务器端分页
            searching: false, //禁用原生搜索
            orderMulti: false, //启用多列排序
            order: [], //取消默认排序查询,否则复选框一列会出现小箭头
            renderer: "bootstrap", //渲染样式：Bootstrap和jquery-ui
            pagingType: "simple_numbers", //分页样式：simple,simple_numbers,full,full_numbers
            columnDefs: [{
                "targets": 'nosort', //列的样式名
                "orderable": false //包含上样式名‘nosort'的禁止排序
            }],
            ajax: function (data, callback, settings) {
                //封装请求参数
                var param = {};
                param.pageSize = data.length;//页面显示记录条数，在页面显示每页显示多少项的时候
                param.start = data.start;//开始的记录序号
                param.currentPage = (data.start / data.length) + 1;//当前页码
                param.action = 'search';
                param.w_no = w_no;
                //console.log(param);
                //ajax请求数据
                $.ajax({
                    type: "GET",
                    url: "/api/v1.0/waybills/operator/index",
                    cache: false, //禁用缓存
                    data: param, //传入组装的参数
                    dataType: "json",
                    success: function (result) {
                        if(result.errno == "0") {
                            var returnData = {};
                            returnData.draw = data.startRow;//这里直接自行返回了draw计数器,应该由后台返回
                            returnData.recordsTotal = result.totalRows;//返回数据全部记录
                            returnData.recordsFiltered = result.totalRows;//后台不实现过滤功能，每次查询均视作全部结果
                            returnData.data = result.data ;//返回的数据列表
                            //此时的数据需确保正确无误，异常判断应在执行此回调前自行处理完毕
                            callback(returnData);
                        } else {
                            alert(result.errmsg)
                        }
                    }
                });
            },
            "columns": [
                //跟你要显示的字段是一一对应的。
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                         return "<a href='/operator/waybill/edit.html?id="+ data.id + "'>修改" + "</a>&nbsp;&nbsp;<a href='#' id='delwaybill_"+ data.id + "' onclick=delete_waybill(this);>删除" + "</a>";
                    }
                },
                {'data': 'w_no'
                },
                {'data': 'seller'
                },
                {'data': 'depot'
                },
                {'data': 'customs_apply'
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        if(data.lading_bill != null){
                            return "<a href='#' id='billing_"+ data.id + "' onclick=show_billing(this);>查看" + "</a>&nbsp;&nbsp;<a href='#' id='delbilling_"+ data.id + "' onclick=delete_billing(this);>删除" + "</a>";
                        } else {
                            return "<a href='/operator/waybill/lading_bill_upload.html?id="+ data.id + "'>上传" + "</a>";
                        }
                    }
                },
                {'data': '',  "orderable": false
                },
                {'data': 'delivery_time'
                },
                {'data': 'etd'
                },
                {'data': 'eta'
                },
                {'data': 'customs_declaration'
                },
                {'data': 'depot_status'
                },
                {'data': 'cont_num'
                },
                {'data': 'real_weight'
                },
                {'data': 'volume_weight'
                },
                {'data': 'billing_weight'
                },
                {'data': 'fare'
                },
                {'data': 'declared_value'
                },
            ],
            "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull)            {                    //列样式处理
            }
        })
        .api();


})