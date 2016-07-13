# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from api.models import TaskList
from instance.models import Instance
from server.models import Server, SBasicStat
from server.models import IosTemplate
from server.models import VmFile
from django.db.models import Q
import json


# Create your views here.
@login_required
def server_list(request):
    errors = list([])
    if request.method == 'GET':
        order_by = request.GET.get('order_by', 'sn')
        sort = request.GET.get('sort', 'up')
        word = request.GET.get('word', '')

        if sort == 'down':
            new_sort = 'up'
            order_str = '-' + order_by
        else:
            new_sort = 'down'
            order_str = order_by

        try:
            word = json.loads(word)
        except:
            word = word

        all_servers = Server.objects.all().count()
        online_servers = Server.objects.filter(status=1).count()

        if '' == word:
            hosts_info = Server.objects.filter().order_by(order_str)
        elif isinstance(word, int):
            hosts_info = Server.objects.filter(status=word).order_by(order_str)
        else:
            hosts_info = Server.objects.filter(
                Q(sn=word) | Q(name__contains=word) | Q(alias__contains=word)
            ).order_by(order_str)

        return render(request, 'server/server_list.html',
                      {
                          'sort': new_sort,
                          'word': word,
                          'all_servers': all_servers,
                          'online_servers': online_servers,
                          'hosts_info': hosts_info
                      })
    else:
        errors.append('你咋发的不是GET, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})


@login_required
def server_info(request, sn, tab):
    data = list([])
    iostemp_list = list([])
    vm_files_list = list([])

    errors = list([])
    if request.method == 'GET':
        if Server.objects.filter(sn=sn).count():
            name = Server.objects.get(sn=sn).name
            if tab != 'packages':
                iostemp_list = IosTemplate.objects.filter(server__sn=sn)
            else:
                vm_files_list = VmFile.objects.filter(server__sn=sn)

            if tab == 'logs':
                data.append('logs')
            elif tab == 'instances':
                data = Instance.objects.filter(server__sn=sn)
            elif tab == 'tasks_all':
                data.append(TaskList.objects.order_by('-create_time').filter(server__sn=sn))
                data.append(['创建未发布', '发布未领取', '领取未完成', '完成且成功', '完成却失败', '取消'])
            elif tab == 'tasks':
                # data[0] 创建未发布任务清单
                data.append(TaskList.objects.order_by('-create_time').filter(server__sn=sn, status=0))

                # data[1] 发布未领取任务清单
                data.append(TaskList.objects.order_by('-create_time').filter(server__sn=sn, status=1))

                # data[2] 领取处理中任务清单
                data.append(TaskList.objects.order_by('-create_time').filter(server__sn=sn, status=2))

                # data[3] 取消任务清单
                data.append(TaskList.objects.order_by('-create_time').filter(server__sn=sn, status=5))

                # data[4] 领取已完成任务清单
                data.append(TaskList.objects.order_by('-create_time').filter(Q(server__sn=sn), Q(status=3) | Q(status=4)))

            elif tab == 'setting':
                data.append('setting')
            elif tab == 'packages':
                data = IosTemplate.objects.filter(server__sn=sn)
            else:
                tab = 'overview'
                # ------ 顶部状态
                # 服务器基本信息 data[0]
                data.append(Server.objects.get(sn=sn))

                # 服务器最近的状态信息 data[1]
                basic_stat = dict({})
                try:
                    basic_stat['cpu'] = SBasicStat.objects.filter(server__sn=sn, stat_type='cpu_used').last().value
                except:
                    basic_stat['cpu'] = 0
                try:
                    basic_stat['disk'] = SBasicStat.objects.filter(server__sn=sn, stat_type='disk_used').last().value
                except:
                    basic_stat['disk'] = 0
                try:
                    basic_stat['mem'] = SBasicStat.objects.filter(server__sn=sn, stat_type='mem_used').last().value
                except:
                    basic_stat['mem'] = 0

                # 在线虚拟机数量
                basic_stat['runserver'] = Instance.objects.filter(status=1, server__sn=sn).count()
                data.append(basic_stat)

                # ------ 业务详情
                # VM_files详情 data[2]
                vm_files = VmFile.objects.filter(server__sn=sn)
                data.append(vm_files)

                # 任务详情 data[3]
                task_info = dict({})
                task_info["task0"] = TaskList.objects.filter(server__sn=sn, status=0).count()
                task_info["task1"] = TaskList.objects.filter(server__sn=sn, status=1).count()
                task_info["task2"] = TaskList.objects.filter(server__sn=sn, status=2).count()
                task_info["task3"] = TaskList.objects.filter(server__sn=sn, status=3).count()
                task_info["task4"] = TaskList.objects.filter(server__sn=sn, status=4).count()
                task_info["task5"] = TaskList.objects.filter(server__sn=sn, status=5).count()
                data.append(task_info)

            return render(request, 'server/server_info.html',
                          {'name': name,
                           'sn': sn,
                           'tab': tab,
                           'data': data,
                           'iostemp_list': iostemp_list,
                           'vm_files_list': vm_files_list
                           })
        else:
            return render_to_response('444.html', {'errors': ['SN不存在']})
    else:
        errors.append('你咋发的不是GET, 搞笑啊!!!')
        return render(request, '444.html', {'errors': errors})