/**
 *
 * @authors Crazw (craazw@gmail.com)
 * @date    2015-05-12 21:00:24
 * @version 0.0.1
 */

//等网页加载完毕再执行
window.onload = function  () {
    $(function(){
        $(".recover-snap").click(function(){
            $("#basicTaskModal").modal();

            // 修改提交地址
            $("#basicTaskModal").find(".form-horizontal").attr('action', '/api/instance/');

            // 修改标题
            $("#basicTaskModal").find(".modal-title").html('恢复快照');

            // 先清空再添加元素
            var body = $("#basicTaskModal").find(".modal-body");
            body.empty()

            // 赋值
            var sn = $(this).parents(".father-opt").find(".sn").html();
            var name = $(this).parents(".father-opt").find(".name").html();
            var snap_name = $(this).parents(".father-opt").find(".snap_name").html();
            var snap_mem_size = $(this).parents(".father-opt").find(".snap_mem_size").html();

            body.append( '<p class="text-center">确定执行恢复虚拟机**' + name + '**的快照操作?</p>' )
            body.append( newHiddenDiv("sn") );
            $('.sn').val(sn);
            body.append( newHiddenDiv("name") );
            $('.name').val(name);
            body.append( newHiddenDiv("snap_name") );
            $('.snap_name').val(snap_name);
            body.append( newHiddenDiv("snap_mem_size") );
            $('.snap_mem_size').val(snap_mem_size);
            body.append( newHiddenDiv("action") );
            $('.action').val("snapshot");
            body.append( newHiddenDiv("task_type") );
            $('.task_type').val(5);
        });
    });
    $(function(){
        $(".del-snap").click(function(){
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
            var snap_name = $(this).parents(".father-opt").find(".snap_name").html();

            body.append( '<p class="text-center">确定执行恢复虚拟机**' + name + '**的快照操作?</p>' )
            body.append( newHiddenDiv("sn") );
            $('.sn').val(sn);
            body.append( newHiddenDiv("name") );
            $('.name').val(name);
            body.append( newHiddenDiv("snap_name") );
            $('.snap_name').val(snap_name);
            body.append( newHiddenDiv("action") );
            $('.action').val("snapshot");
            body.append( newHiddenDiv("task_type") );
            $('.task_type').val(7);
        });
    });

    // 添加虚拟机配置
	$(function(){
		$(".add-setting").click(function(){
			$("#addSetting").modal();

			//获得当前版本
			var sn = $(this).parents(".father-opt").find(".sn").html();
			var name = $(this).parents(".father-opt").find(".name").html();

            // 设置隐藏属性
            $('.sn').val(sn);
            $('.name').val(name);

            // 设置其他参数
			$('.now-sn').html(sn);
			$('.now-name').html(name);
		});
	});

	// 虚拟机网络配置
	$(function(){
		$(".set-net").click(function(){
			$("#setNet").modal();

			//获得当前版本
			var sn = $(this).parents(".father-opt").find(".sn").html();
			var name = $(this).parents(".father-opt").find(".name").html();

            // 设置隐藏属性
            $('.sn').val(sn);
            $('.name').val(name);

            // 设置其他参数
			$('.now-sn').html(sn);
			$('.now-name').html(name);
		});
	});
}