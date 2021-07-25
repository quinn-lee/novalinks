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
    conf = confirm("确认要删除已经存在的提单文件吗？");
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

function show_pod(obj) {
    $.ajax({
        url:"/api/v1.0/waybills/show_pod?id="+obj.id.split("_")[1],
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

function delete_pod(obj) {
    conf = confirm("确认要删除已经存在的POD文件吗？");
    if (conf == false) {
        return
    }
    $.ajax({
        url:"/api/v1.0/waybills/delete_pod?id="+obj.id.split("_")[1],
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
                param.customs_declaration = 0;
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
                         return "<a title='修改运单信息' href='/operator/waybill/edit.html?id="+ data.id + "'><i class='mdi mdi-table-edit text-success'></i>" + "</a>&nbsp;&nbsp;<a title='删除运单' href='#' id='delwaybill_"+ data.id + "' onclick=delete_waybill(this);><i class='mdi mdi-delete-forever text-danger'></i>" + "</a>";
                    }
                },
                {'data': null, "orderable": false,
                    render: function (data, type, full) {
                        html_str = ""
                        for(var key in data.wms_info){
                            html_str = html_str + "<a class='dropdown-item'>" + key + "：" + data.wms_info[key] + "</a>"
                        }
                        if(html_str == ""){
                            html_str = "<a class='dropdown-item'>暂时没有获取到预报信息</a>"
                        }
                        return "<div class='dropdown'><a class='btn btn-secondary dropdown-toggle p-0 bg-transparent border-0 text-dark shadow-none font-weight-medium' href='#' style='font-size: 12px;' role='button' id='dropdownMenuLinkA' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'><span class='mb-0 d-inline-block'>" + data.w_no + "</span></a><div class='dropdown-menu' aria-labelledby='dropdownMenuLinkA'>" + html_str + "</div></div>"
                    }
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        if(data.wms_user != null){
                            return data.seller + "</br>(" + data.wms_user + ")";
                        } else {
                            return data.seller;
                        }
                    }
                },
                {'data': 'depot',  "orderable": false
                },
                {'data': 'customs_apply',  "orderable": false
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        if(data.lading_bill != null){
                            return "<a title='查看提单' href='#' id='billing_"+ data.id + "' onclick=show_billing(this);><i class='mdi mdi-download text-success'></i>" + "</a>&nbsp;&nbsp;<a title='删除提单' href='#' id='delbilling_"+ data.id + "' onclick=delete_billing(this);><i class='mdi mdi-delete-forever text-danger'></i>" + "</a>";
                        } else {
                            return "<a title='上传提单' href='/operator/waybill/lading_bill_upload.html?id="+ data.id + "'><i class='mdi mdi-upload text-success'></i>" + "</a>";
                        }
                    }
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        html_str = ""
                        for(var i=0;i<data.tracking_infos.length;i++){
                            html_str = html_str + "<a class='dropdown-item'><div class='item-content flex-grow'><h6 class='ellipsis font-weight-normal'>" + data.tracking_infos[i].event_time + "&nbsp;&nbsp;" + data.tracking_infos[i].location + "</h6><p class='font-weight-light small-text text-muted mb-0'>" + data.tracking_infos[i].event + "&nbsp;&nbsp;" + data.tracking_infos[i].description + "</p></div></a>"
                        }
                        if (html_str != ""){
                            html_str = "<a title='查看物流轨迹' style='margin-right: 5px;' id='messageDropdown' href='#' data-toggle='dropdown'><i class='mdi mdi-message-text mx-0 text-info'></i></a><div class='dropdown-menu dropdown-menu-right navbar-dropdown' aria-labelledby='messageDropdown'>" + html_str + "</div>"
                        }
                        return html_str + "<a title='新增物流轨迹' href='/operator/waybill/new_tracking_info.html?id="+ data.id + "'><i class='mdi mdi-message-plus text-success'></i>" + "</a>";

                    }
                },
                {'data': 'delivery_time', "orderable": false,
                    render: function (data, type, full) {
                        if(data != null){
                            return data.split(" ").join("</br>");
                        }
                    }
                },
                {'data': 'etd',  "orderable": false,
                    render: function (data, type, full) {
                        if(data != null){
                            return data.split(" ").join("</br>");
                        }
                    }
                },
                {'data': 'eta',  "orderable": false,
                    render: function (data, type, full) {
                        if(data != null){
                            return data.split(" ").join("</br>");
                        }
                    }
                },
                {'data': null, "orderable": false,
                    render: function (data, type, full) {
                        if(data.agent_info != null){
                            return "<div class='dropdown'><a class='btn btn-secondary dropdown-toggle p-0 bg-transparent border-0 text-dark shadow-none font-weight-medium' href='#' style='font-size: 12px;' role='button' id='dropdownMenuLinkA' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'><span class='mb-0 d-inline-block'>" + data.customs_declaration + "</span></a><div class='dropdown-menu' aria-labelledby='dropdownMenuLinkA'><a class='dropdown-item'>代理信息：<span>" + data.agent_info + "</span></a></div></div>";
                        } else {
                            return data.customs_declaration;
                        }
                    }
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        if(data.pod != null){
                            return data.depot_status+"&nbsp;<a title='查看POD' href='#' id='pod_"+ data.id + "' onclick=show_pod(this);><i class='mdi mdi-download text-success'></i>POD" + "</a>&nbsp;&nbsp;<a title='删除POD' href='#' id='delpod_"+ data.id + "' onclick=delete_pod(this);><i class='mdi mdi-delete-forever text-danger'></i>POD" + "</a>";
                        } else {
                            return data.depot_status+"&nbsp;<a title='上传POD' href='/operator/waybill/pod_upload.html?id="+ data.id + "'><i class='mdi mdi-upload text-success'></i>POD" + "</a>";
                        }
                    }
                },
                {'data': 'cont_num',  "orderable": false
                },
                {'data': 'real_weight',  "orderable": false
                },
                {'data': 'volume_weight',  "orderable": false
                },
                {'data': 'billing_weight',  "orderable": false
                },
                {'data': 'fare',  "orderable": false
                },
                {'data': 'declared_value',  "orderable": false
                },
            ],
            "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull)            {                    //列样式处理
            }
        })
        .api();


})