/**
 *
 * @authors Crazw (craazw@gmail.com)
 * @date    2015-05-12 21:00:24
 * @version 0.0.1
 */

// text框
var newTextDiv = function(options){
    var html = '<div class="form-group ';

    if(options.require == true)
        html += 'required';

    html += '"><label class="col-sm-4 control-label">' +
        options.label + '</label><div class="col-sm-6"><input type="text" name="' +
        options.name + '" class="form-control" placeholder="' + options.pla + '" '
    if(options.pattern)
        html += 'pattern="' + options.pattern + '" '
    html +='></div></div>';
    return $(html);
};

//hidden隐藏属性
var newHiddenDiv = function(option){
    return '<input type="hidden" class="' + option + '" name="' + option + '">';
};

//disable的文本属性
var newDisableDiv = function(options){
    return '<div class="form-group"><label class="col-sm-4 control-label">' + options.label + '</label><div class="col-sm-6"><label class="' + options.class_name +'" for="disabledTextInput" style="padding: 8px;"></label></div></div>'
};

//一个填写框的modal
var basic_modal_temp = function(options){
    $("#basicModal").modal();

    // 修改提交地址
    $("#basicModal").find(".form-horizontal").attr('action', options.url);

    // 修改标题
    $("#basicModal").find(".modal-title").html(options.title);

    // 先清空再添加元素
    var body = $("#basicModal").find(".modal-body");
    body.empty()

    // 赋值
    body.append( newHiddenDiv("sn") );
    $('.sn').val(options.sn);
    body.append( newHiddenDiv("action") );
    $('.action').val(options.field);
    body.append( newDisableDiv({label: '设备SN', class_name: 'now-sn'}) )
    $('.now-sn').html(options.sn);
    body.append( newTextDiv({ require: true, label: options.label, name: 'value', pla: options.pla }) );
};

//添加虚拟机
$(function(){
    $(".create-ins").click(function(){
        $("#createIns").modal();
        var sn = $(this).parents(".father-opt").find(".sn").html();
        $('.now-sn').html(sn);
        $('.sn').val(sn);
    });
});

//关闭虚拟机
$(function(){
    $(".ins-stop").click(function(){
        $("#basicTaskModal").modal();

        // 修改提交地址
        $("#basicTaskModal").find(".form-horizontal").attr('action', '/api/instance/');

        // 修改标题
        $("#basicTaskModal").find(".modal-title").html('关闭虚拟机');

        // 先清空再添加元素
        var body = $("#basicTaskModal").find(".modal-body");
        body.empty()

        // 赋值
        var sn = $(this).parents(".father-opt").find(".sn").html();
        var name = $(this).parents(".father-opt").find(".name").html();
        body.append( '<p class="text-center">确定执行关闭虚拟机**' + name + '**的操作?</p>' )
        body.append( newHiddenDiv("sn") );
        $('.sn').val(sn);
        body.append( newHiddenDiv("name") );
        $('.name').val(name);
        body.append( newHiddenDiv("action") );
        $('.action').val("stop");
    });
});

//启动虚拟机
$(function(){
    $(".ins-start").click(function(){
        $("#basicTaskModal").modal();

        // 修改提交地址
        $("#basicTaskModal").find(".form-horizontal").attr('action', '/api/instance/');

        // 修改标题
        $("#basicTaskModal").find(".modal-title").html('开启虚拟机');

        // 先清空再添加元素
        var body = $("#basicTaskModal").find(".modal-body");
        body.empty()

        // 赋值
        var sn = $(this).parents(".father-opt").find(".sn").html();
        var name = $(this).parents(".father-opt").find(".name").html();
        body.append( '<p class="text-center">确定执行开启虚拟机**' + name + '**的操作?</p>' )
        body.append( newHiddenDiv("sn") );
        $('.sn').val(sn);
        body.append( newHiddenDiv("name") );
        $('.name').val(name);
        body.append( newHiddenDiv("action") );
        $('.action').val("start");
    });
});

//虚拟机创建快照
$(function(){
    $(".ins-snapshot").click(function(){
        $("#basicTaskModal").modal();

        // 修改提交地址
        $("#basicTaskModal").find(".form-horizontal").attr('action', '/api/instance/');

        // 修改标题
        $("#basicTaskModal").find(".modal-title").html('创建快照');

        // 先清空再添加元素
        var body = $("#basicTaskModal").find(".modal-body");
        body.empty()

        // 赋值
        var sn = $(this).parents(".father-opt").find(".sn").html();
        var name = $(this).parents(".father-opt").find(".name").html();
        body.append( newHiddenDiv("sn") );
        $('.sn').val(sn);
        body.append( newDisableDiv({label: '设备SN', class_name: 'now-sn'}) )
        $('.now-sn').html(sn);
        body.append( newDisableDiv({label: '设备SN', class_name: 'now-name'}) )
        $('.now-name').html(name);
        body.append( newTextDiv({ require: true, label: '快照名称', name: 'snap_name', pla: '输入快照名称', pattern: '[a-z][\\w]{2,19}$' }) );

        body.append( newHiddenDiv("name") );
        $('.name').val(name);
        body.append( newHiddenDiv("action") );
        $('.action').val("snapshot");
        body.append( newHiddenDiv("task_type") );
        $('.task_type').val(4);
    });
});

//删除虚拟机
$(function(){
    $(".ins-delete").click(function(){
        $("#basicTaskModal").modal();

        // 修改提交地址
        $("#basicTaskModal").find(".form-horizontal").attr('action', '/api/instance/');

        // 修改标题
        $("#basicTaskModal").find(".modal-title").html('删除虚拟机');

        // 先清空再添加元素
        var body = $("#basicTaskModal").find(".modal-body");
        body.empty()

        // 赋值
        var sn = $(this).parents(".father-opt").find(".sn").html();
        var name = $(this).parents(".father-opt").find(".name").html();
        body.append('<div class="form-group required"> <label class="col-sm-4 control-label">是否删除磁盘</label> <div class="col-sm-6"> <select name="del-disk" class="form-control"> <option value ="0">删除</option> <option value ="1">保留</option> </select> </div> </div>');

        body.append( newHiddenDiv("sn") );
        $('.sn').val(sn);
        body.append( newHiddenDiv("name") );
        $('.name').val(name);
        body.append( newHiddenDiv("action") );
        $('.action').val("delete");
    });
});