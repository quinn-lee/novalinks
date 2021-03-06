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
    var barcode = queryData["barcode"];
    if(sku_code==undefined){
        sku_code = ""
    }
    if(barcode==undefined){
        barcode = ""
    }

    $("#nord_code").val(nord_code)
    $("#sku_code").val(sku_code)
    $("#barcode").val(barcode)
    if (!nord_code || nord_code == undefined) {
        location.href = "/inspector/users/index.html";
    }
    $(".inv.nav-link").each(function(){
		href = $(this).attr('href')
		$(this).attr('href', href+"?nord_code="+nord_code)
	});

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
                param.nord_code = nord_code;
                param.sku_code = sku_code;
                param.barcode = barcode;
                //console.log(param);
                //ajax请求数据
                $.ajax({
                    type: "GET",
                    url: "/api/v1.0/users/wms_inventories",
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
                {'data': 'sku_code',  "orderable": false
                },
                {'data': 'barcode',  "orderable": false
                },
                {'data': 'name',  "orderable": false
                },
                {'data': 'saleable_quantity',  "orderable": false
                },
                {'data': 'frozen_quantity',  "orderable": false
                },
                {'data': 'problem_quantity',  "orderable": false
                },
                {'data': null,  "orderable": false,
                    render: function (data, type, full) {
                        if(data.price != null){
                            return data.price + "&nbsp;&nbsp;&nbsp;<a title='修改运单信息' href='/inspector/users/edit_price.html?nord_code="+ nord_code + "&sku_code="+ data.sku_code + "&price=" + data.price + "'>修改价格</a>";
                        } else {
                            return "<a title='修改运单信息' href='/inspector/users/edit_price.html?nord_code="+ nord_code + "&sku_code="+ data.sku_code + "&price='>修改价格</a>";
                        }
                    }
                },
            ],
            "fnRowCallback": function (nRow, aData, iDisplayIndex, iDisplayIndexFull)            {                    //列样式处理
            }
        })
        .api();


})