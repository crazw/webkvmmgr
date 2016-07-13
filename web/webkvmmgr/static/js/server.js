/**
 *
 * @authors Crazw (craazw@gmail.com)
 * @date    2015-05-12 21:00:24
 * @version 0.0.1
 */

//等网页加载完毕再执行
window.onload = function  () {
	//修改设备别名
	$(function(){
		$(".rename-alias").click(function(){
		    var sn = $(this).parents(".father-opt").find(".sn").html();
            basic_modal_temp({
                sn: sn,
                url: '/api/server/',
                title: '修改设备别名',
                field: 'alias',
                label: '新的别名',
                pla: '清华CDS01'
            })
		});
	});

	//修改设备单位名称
	$(function(){
		$(".rename-name").click(function(){
		    var sn = $(this).parents(".father-opt").find(".sn").html();
            basic_modal_temp({
                sn: sn,
                url: '/api/server/',
                title: '修改设备单位名称',
                field: 'name',
                label: '新的单位名称',
                pla: '清华大学'
            })
		});
	});

	//设备其他详情
	$(function(){
		$(".server-main-info").click(function(){
            $("#basicModal").modal();

            // 修改提交地址
            $("#basicModal").find(".form-horizontal").attr('action', '#');

            // 修改标题
            $("#basicModal").find(".modal-title").html('设备详情信息');

            // 先清空再添加元素
            var body = $("#basicModal").find(".modal-body");
            body.empty()

            // 赋值
            var sn = $(this).parents(".father-opt").find(".sn").html();
            body.append( newDisableDiv({label: '设备SN', class_name: 'now-sn'}) )
            $('.now-sn').html(sn);

            var ip = $(this).parents(".father-opt").find(".ip").html();
            body.append( newDisableDiv({label: "出口IP", class_name: 'ip'}) )
            $('.ip').html(ip)

            var architecture = $(this).parents(".father-opt").find(".architecture").html();
            body.append( newDisableDiv({label: "系统位数", class_name: 'architecture'}) )
            $('.architecture').html(architecture)

            var version = $(this).parents(".father-opt").find(".version").html();
            body.append( newDisableDiv({label: "业务包版本", class_name: 'version'}) )
            $('.version').html(version)

            var libvirt_version = $(this).parents(".father-opt").find(".libvirt_version").html();
            body.append( newDisableDiv({label: "libvirt版本", class_name: 'libvirt_version'}) )
            $('.libvirt_version').html(libvirt_version)

            var hv_version = $(this).parents(".father-opt").find(".hv_version").html();
            body.append( newDisableDiv({label: "hypervisor版本", class_name: 'hv_version'}) )
            $('.hv_version').html(hv_version)

            var cpu_name = $(this).parents(".father-opt").find(".cpu_name").html();
            body.append( newDisableDiv({label: "CPU名称", class_name: 'cpu_name'}) )
            $('.cpu_name').html(cpu_name)

		});
	});

    //添加虚拟机
    $(function(){
        $(".create-ins").click(function(){
            $("#createIns").modal();
            var sn = $(this).parents(".father-opt").find(".sn").html();
            $('.now-sn').html(sn);
            $('.sn').val(sn);
        });
    });

    //添加镜像模板
    $(function(){
        $(".create-ios-temp").click(function(){
            $("#createIosTemp").modal();

            var sn = $(this).parents(".father-opt").find(".sn").html();
            $('.now-sn').html(sn);
            $('.sn').val(sn);

        });
    });

    //添加ISO
	$(function(){
		$(".add-vmfile").click(function(){
			$("#addVmFile").modal();

			//获得当前版本
			var sn = $(this).parents(".father-opt").find(".sn").html();
            // 设置隐藏属性
            $('.sn').val(sn);

            // 设置其他参数
			$('.now-sn').html(_now_sn);
		});
	});

    //删除镜像模板
	$(function(){
		$(".iostemp-delete").click(function(){
            $("#basicModal").modal();

            // 修改提交地址
            $("#basicModal").find(".form-horizontal").attr('action', '/api/iostemp/');

            // 修改标题
            $("#basicModal").find(".modal-title").html('删除镜像模板');

            // 先清空再添加元素
            var body = $("#basicModal").find(".modal-body");
            body.empty()

            // 赋值
            var id = $(this).parents(".father-opt").find(".id").html();
            body.append( newHiddenDiv("id") );
            $('.id').val(id);

            body.append( newHiddenDiv("action") );
            $('.action').val("delete");

            var sn = $(this).parents(".father-opt").find(".sn").html();
            body.append( newHiddenDiv("sn") );
            $('.sn').val(sn);
            body.append( newDisableDiv({label: '设备SN', class_name: 'now-sn'}) )
            $('.now-sn').html(sn);

            var name = $(this).parents(".father-opt").find(".name").html();
            body.append( newDisableDiv({label: "镜像模板名称", class_name: 'name'}) )
            $('.name').html(name)

		});
	});
}