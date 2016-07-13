# coding=utf-8
import datetime
import uuid
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from api.models import TaskType, TaskList, AddIns, AddVmFile, CtrlIns, SnapIns, DelIns, SettingIns, SetNetIns
from instance.models import Instance
from server.models import Server, VmFile, IosTemplate


def task_basic_info(options):
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    server = Server.objects.get(sn=options['sn'])
    task_type = TaskType.objects.get(type=options['task_type'])
    if 'name' in options:
        instance = Instance.objects.get(name=options['name'])
    else:
        instance = None
    try:
        rs = TaskList.objects.create(
            server=server, instance=instance, type=task_type,
            create_time=create_time, status=options['status']
        )
    except Exception, e:
        return e
    else:
        return str(rs.uuid)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        keep_account = request.POST.get('keep-account', 'off')
        # todo: session相关的功能补充

        # 判断用户名和密码是否正确
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/server/list')
        else:
            error_msg = "登录失败, 用户名或密码错误!"
            return render(request, 'login.html', {'error_msg': error_msg})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect('/server/list')
        else:
            return render(request, 'login.html', {})


@login_required
def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login")


# 服务器端相关的更新
@login_required
def server_api(request):
    errors = list([])
    sn = value = action = ''
    if request.method == 'POST':
        if not request.POST.get('sn', ''):
            errors.append('更新失败! SN字段不存在!')
        else:
            sn = str(request.POST.get('sn')).strip()

        if not request.POST.get('action', ''):
            errors.append('更新失败! action字段不存在!')
        else:
            action = str(request.POST.get('action')).strip()

        if not request.POST.get('value', ''):
            errors.append('更新失败! 字段更新的值不存在!')
        else:
            value = request.POST.get('value')

        if not errors:
            try:
                Server.objects.filter(sn=sn).update(**{action: value})
            except Exception, e:
                errors.append(e)
                return render(request, '444.html', {'errors': errors})
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return render(request, '444.html', {'errors': errors})
    else:
        errors.append('你咋发的不是POST, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})


@login_required
def instance_api(request):
    errors = list([])
    sn = action = ''
    if request.method == 'POST':
        if not request.POST.get('sn', ''):
            errors.append('更新失败! SN字段不存在!')
        else:
            sn = str(request.POST.get('sn')).strip()

        if not request.POST.get('action', ''):
            errors.append('更新失败! action字段不存在!')
        else:
            action = str(request.POST.get('action')).strip()

        if not errors:
            if action == 'create':
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 1
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    iostemp = str(request.POST.get('iostemp', ''))
                    vm_name = str(request.POST.get('name', ''))
                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)

                    # 获取创建虚拟机的配置信息
                    iostemp_info = IosTemplate.objects.get(server__sn=sn, name=iostemp)
                    vm_file = iostemp_info.vm_file
                    cpu_num = iostemp_info.cpu_num
                    cpu_model = iostemp_info.cpu_model
                    disk_model = iostemp_info.disk_model
                    sys_disk_size = iostemp_info.sys_disk_size
                    data_disk_size = iostemp_info.data_disk_size
                    mem_size = iostemp_info.mem_size

                    try:
                        AddIns.objects.create(
                            uuid=task_uuid, vm_name=vm_name, vm_file=vm_file, mem_size=mem_size,
                            cpu_num=cpu_num, cpu_model=cpu_model, disk_model=disk_model,
                            sys_disk_size=sys_disk_size, data_disk_size=data_disk_size
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})

            elif action == 'delete':
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 3
                options['name'] = str(request.POST.get('name', ''))
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    del_disk = str(request.POST.get('del-disk', ''))
                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        DelIns.objects.create(
                            uuid=task_uuid, del_disk=del_disk
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        # 删除虚拟机后, 更新设备锁状态: islock
                        try:
                            Instance.objects.filter(server__sn=options['sn'], name=options['name']).update(islock=0)
                        except Exception, e:
                            errors.append('更新虚拟机锁字段失败,错误: ' + str(e) + '!!!')
                            return render(request, '444.html', {'errors': errors})
                        else:
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})

            elif action == 'snapshot':
                options = dict({})
                options['sn'] = sn
                options['task_type'] = int(request.POST.get('task_type', ''))
                options['name'] = str(request.POST.get('name', ''))
                if options['task_type'] == 5:
                    snap_mem_size = int(request.POST.get('snap_mem_size', ''))
                    if snap_mem_size > Instance.objects.get(server__sn=options['sn'], name=options['name']).mem_size:
                        errors.append('快照内存比现内存大, 无法恢复!!!')
                        return render(request, '444.html', {'errors': errors})

                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    snap_name = str(request.POST.get('snap_name', ''))
                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        SnapIns.objects.create(
                            uuid=task_uuid, snap_name=snap_name
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        # 如果是恢复快照, 更新虚拟机锁字段: islock
                        if options['task_type'] == 5:
                            try:
                                Instance.objects.filter(server__sn=options['sn'], name=options['name']).update(islock=0)
                            except Exception, e:
                                errors.append('更新虚拟机锁字段失败,错误: ' + str(e) + '!!!')
                                return render(request, '444.html', {'errors': errors})
                            else:
                                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                        else:
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})

            elif action == 'stop' or action == 'start':
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 20
                options['name'] = str(request.POST.get('name', ''))
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    action = str(request.POST.get('action', ''))
                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        CtrlIns.objects.create(
                            uuid=task_uuid, action=action
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})
            elif action == 'add_setting':
                print request.POST
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 2
                options['name'] = str(request.POST.get('name', ''))
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    # 获取旧的配置信息
                    old_cpu_num = Instance.objects.get(server__sn=options['sn'], name=options['name']).cpu_num
                    old_mem_size = Instance.objects.get(server__sn=options['sn'], name=options['name']).mem_size
                    if request.POST.get('new_cpu') == '':
                        new_cpu_num = old_cpu_num
                    else:
                        new_cpu_num = int(request.POST.get('new_cpu'))

                    if request.POST.get('new_mem') == '':
                        new_mem_size = old_mem_size
                    else:
                        new_mem_size = float(request.POST.get('new_mem')) * 1024 * 1024

                    if request.POST.get('add-data-disk') == '':
                        datadisk_extend = 0
                    else:
                        datadisk_extend = int(request.POST.get('add-data-disk')) * 1024 * 1024 * 1024

                    if request.POST.get('add-sys-disk') == '':
                        sysdisk_extend = 0
                    else:
                        sysdisk_extend = int(request.POST.get('add-sys-disk')) * 1024 * 1024 * 1024

                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        SettingIns.objects.create(
                            uuid=task_uuid, new_cpu_num=new_cpu_num, new_mem_size=new_mem_size,
                            datadisk_extend=datadisk_extend, sysdisk_extend=sysdisk_extend
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})
            elif action == 'set_net':
                print request.POST
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 8
                options['name'] = str(request.POST.get('name', ''))
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)
                if uuid.UUID(rs, version=4):
                    nic_name = request.POST.get('nic_name')
                    bootproto = request.POST.get('bootproto')
                    if bootproto == 'static':
                        ip = request.POST.get('ip')
                        netmask = request.POST.get('netmask')
                        gateway = request.POST.get('gateway')
                        dns = request.POST.get('dns')
                    else:
                        ip = ''
                        netmask = ''
                        gateway = ''
                        dns = ''

                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        SetNetIns.objects.create(
                            uuid=task_uuid, nic_name=nic_name, bootproto=bootproto,
                            ip=ip, netmask=netmask, gateway=gateway, dns=dns
                        )
                    except Exception, e:
                        errors.append(e)
                        return render(request, '444.html', {'errors': errors})
                    else:
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})
        else:
            return render(request, '444.html', {'errors': errors})
    else:
        errors.append('你咋发的不是POST, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})


@login_required
def iostemp_api(request):
    errors = list([])
    sn = action = ''
    if request.method == 'POST':
        if not request.POST.get('sn', ''):
            errors.append('更新失败! SN字段不存在!')
        else:
            sn = str(request.POST.get('sn')).strip()

        if not request.POST.get('action', ''):
            errors.append('更新失败! action字段不存在!')
        else:
            action = str(request.POST.get('action')).strip()

        if not errors:
            if action == 'create':
                name = request.POST.get('name', '')
                os = request.POST.get('os', '')
                cpu_num = int(request.POST.get('cpu_num', ''))
                cpu_model = int(request.POST.get('cpu_model', ''))
                sys_disk_size = int(request.POST.get('sys_disk_size', ''))
                data_disk_size = int(request.POST.get('data_disk_size', ''))
                disk_model = int(request.POST.get('disk_model', ''))
                mem_size = int(request.POST.get('mem_size', ''))
                comment = request.POST.get('comment', '')
                if sn == '' or name == '' or os == '' or cpu_num == '' or cpu_model == '' \
                        or sys_disk_size == '' or data_disk_size == '' or disk_model == '' \
                        or mem_size == '':
                    errors.append("必要字段为空, 请仔细检查!!!")
                    return render(request, '444.html', {'errors': errors})

                sys_disk_size = sys_disk_size * 1024 * 1024 * 1024
                data_disk_size = data_disk_size * 1024 * 1024 * 1024
                mem_size = mem_size * 1024 * 1024
                try:
                    server = Server.objects.get(sn=sn)
                    vm_file = VmFile.objects.get(name=os, server__sn=sn)
                    IosTemplate.objects.create(
                        server=server, name=name, cpu_num=cpu_num, cpu_model=cpu_model, vm_file=vm_file,
                        sys_disk_size=sys_disk_size, data_disk_size=data_disk_size, disk_model=disk_model,
                        mem_size=mem_size, comment=comment
                    )
                except Exception, e:
                    errors.append('添加IosTemplate失败,详情: ' + str(e))
                    return render(request, '444.html', {'errors': errors})
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            elif action == 'delete':
                print request.POST
                iostemp_id = request.POST.get('id', '')
                if iostemp_id == '':
                    errors.append("必要字段为空, 请仔细检查!!!")
                    return render(request, '444.html', {'errors': errors})
                try:
                    server = Server.objects.get(sn=sn)
                    IosTemplate.objects.filter(
                        server=server, id=iostemp_id
                    ).delete()
                except Exception, e:
                    errors.append('添加IosTemplate失败,详情: ' + str(e))
                    return render(request, '444.html', {'errors': errors})
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            return render(request, '444.html', {'errors': errors})
    else:
        errors.append('你咋发的不是POST, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})


@login_required
def vmfile_api(request):
    errors = list([])
    sn = action = ''
    if request.method == 'POST':
        if not request.POST.get('sn', ''):
            errors.append('更新失败! SN字段不存在!')
        else:
            sn = str(request.POST.get('sn')).strip()

        if not request.POST.get('action', ''):
            errors.append('更新失败! action字段不存在!')
        else:
            action = str(request.POST.get('action')).strip()

        if not errors:
            if action == 'add':
                # 添加任务相关
                options = dict({})
                options['sn'] = sn
                options['task_type'] = 40
                options['status'] = int(request.POST.get('task_status', '0'))
                rs = task_basic_info(options=options)

                if uuid.UUID(rs, version=4):
                    uri = str(request.POST.get('uri', ''))
                    size = int(request.POST.get('size', ''))
                    vm_format = int(request.POST.get('format', ''))
                    md5 = str(request.POST.get('md5', ''))
                    save_path = str(request.POST.get('save_path', ''))

                    # 获取任务的uuid
                    task_uuid = TaskList.objects.get(uuid=rs)
                    try:
                        AddVmFile.objects.create(
                            uuid=task_uuid, uri=uri, size=size, format=vm_format,
                            md5=md5, save_path=save_path
                        )
                    except Exception, e:
                        errors.append('添加VM File任务失败, ' + str(e) + '!!!')
                        return render(request, '444.html', {'errors': errors})
                    else:
                        # 任务创建成功后, 更新VmFile表相关
                        server = Server.objects.get(sn=options['sn'])
                        name = uri.split('/')[-1]
                        source = 1
                        try:
                            VmFile.objects.create(
                                server=server, name=name, size=size, format=vm_format,
                                path=save_path, source=source, comment='手动添加,还未下载完成'
                            )
                        except Exception, e:
                            errors.append('添加Server表的VMFile信息失败,错误: ' + str(e) + '!!!')
                            return render(request, '444.html', {'errors': errors})
                        else:
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    errors.append('更新任务总列表失败, 错误: ' + rs)
                    return render(request, '444.html', {'errors': errors})

            else:
                pass
        else:
            return render(request, '444.html', {'errors': errors})
    else:
        errors.append('你咋发的不是POST, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})


def stat_api(request):
    pass


def task_api(request):
    errors = list([])
    task_list = list([])
    if request.method == 'POST':
        # 添加虚拟机任务
        add_ins_rs = AddIns.objects.filter(sn=sn, status=0)
        for item in add_ins_rs:
            add_ins = dict({})
            add_ins['id'] = int(item.id)
            add_ins['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            add_ins['father_id'] = str(item.father_id)
            add_ins['age'] = int(item.age)
            add_ins['type'] = int(item.type)
            add_ins['vm_name'] = str(item.vm_name)
            add_ins['topology'] = {"cpu": int(item.cpu_type), "disk": int(item.data_disk_type)}
            add_ins['cpu_num'] = int(item.cpus)
            add_ins['memory'] = int(item.mem) * 1024 * 1024
            add_ins['disk_os'] = int(item.sys_disk) * 1024 * 1024 * 1024
            add_ins['disk_data'] = int(item.data_disk) * 1024 * 1024 * 1024
            add_ins['install_method'] = int(item.install_method)
            add_ins['vm_file'] = str(item.os)
            task_list.append(add_ins)
        # 更新任务状态 1-下发
        add_ins_rs.update(status=1)

        # 删除虚拟机任务
        del_ins_rs = DelIns.objects.filter(sn=sn, status=0)
        for item in del_ins_rs:
            del_ins = dict({})
            del_ins['id'] = int(item.id)
            del_ins['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            del_ins['father_id'] = str(item.father_id)
            del_ins['age'] = int(item.age)
            del_ins['type'] = int(item.type)
            del_ins['vm_name'] = str(item.vm_name)
            del_ins['delete_disk'] = int(item.delete_disk)
            task_list.append(del_ins)
        del_ins_rs.update(status=1)

        # 修改某业务的虚拟机的任务
        set_ins_rs = SettingIns.objects.filter(sn=sn, status=0)
        for item in set_ins_rs:
            set_ins = dict({})
            set_ins['id'] = int(item.id)
            set_ins['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            set_ins['father_id'] = str(item.father_id)
            set_ins['age'] = int(item.age)
            set_ins['type'] = int(item.type)
            set_ins['vm_name'] = str(item.vm_name)
            set_ins['cpu'] = int(item.cpu)
            set_ins['mem'] = int(item.mem)
            set_ins['sysdisk_extend'] = int(item.sysdisk_extend)
            set_ins['datadisk_extend'] = int(item.datadisk_extend)
            task_list.append(set_ins)
        set_ins_rs.update(status=1)

        # 虚拟机的快照相关任务
        snap_ins_rs = SnapIns.objects.filter(sn=sn, status=0)
        for item in snap_ins_rs:
            snap_ins = dict({})
            snap_ins['id'] = int(item.id)
            snap_ins['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            snap_ins['father_id'] = str(item.father_id)
            snap_ins['age'] = int(item.age)
            snap_ins['type'] = int(item.type)
            snap_ins['vm_name'] = str(item.vm_name)
            snap_ins['snapshot_name'] = str(item.snapshot_name)
            task_list.append(snap_ins)
        snap_ins_rs.update(status=1)

        # 控制某业务的虚拟机的任务
        ctrl_ins_rs = CtrlIns.objects.filter(sn=sn, status=0)
        for item in ctrl_ins_rs:
            ctrl_ins = dict({})
            ctrl_ins['id'] = int(item.id)
            ctrl_ins['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            ctrl_ins['father_id'] = str(item.father_id)
            ctrl_ins['age'] = int(item.age)
            ctrl_ins['type'] = int(item.type)
            ctrl_ins['vm_name'] = str(item.vm_name)
            ctrl_ins['action'] = str(item.action)
            task_list.append(ctrl_ins)
        ctrl_ins_rs.update(status=1)

        # 建立下载任务
        down_file_rs = VmFile.objects.filter(sn=sn, status=0)
        for item in down_file_rs:
            down_file = dict({})
            down_file['id'] = int(item.id)
            down_file['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            down_file['father_id'] = str(item.father_id)
            down_file['age'] = int(item.age)
            down_file['type'] = int(item.type)
            down_file['uri'] = str(item.uri)
            down_file['size'] = str(item.size)
            down_file['format'] = str(item.format)
            down_file['md5'] = str(item.md5)
            down_file['save_path'] = str(item.save_path)
            task_list.append(down_file)
        down_file_rs.update(status=1)

        # 网卡配置
        set_net_rs = SetNetIns.objects.filter(sn=sn, status=0)
        for item in set_net_rs:
            set_net = dict({})
            set_net['id'] = int(item.id)
            set_net['create_time'] = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
            set_net['father_id'] = str(item.father_id)
            set_net['age'] = int(item.age)
            set_net['type'] = int(item.type)
            set_net['vm_name'] = str(item.vm_name)
            set_net['nic_name'] = str(item.nic_name)
            set_net['bootproto'] = str(item.bootproto)
            set_net['netmask'] = str(item.netmask)
            set_net['gateway'] = str(item.gateway)
            set_net['dns'] = str(item.dns)
            set_net['ip'] = str(item.ip)
            task_list.append(set_net)
        set_net_rs.update(status=1)

        TaskList.objects.filter(sn=sn, status=0).update(status=1)

    else:
        errors.append('请使用POST请求!')

    if not errors:
        print ''
        print ''
        print '----' * 7 + "下发的任务清单" + '----' * 7
        print '----' * 15
        for i in range(len(task_list)):
            print ''
            print ''
            print task_list[i]
            print ''
            print ''
            print '----' * 15
        print '----' * 7 + "下发的任务清单" + '----' * 7
        print ''
        print ''

        data = dict({})
        data["body"] = task_list

        return JsonResponse(data)
    else:
        return render(request, 'api_error.html', {'errors': errors})
