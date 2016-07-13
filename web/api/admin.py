# coding=utf-8
from django.contrib import admin
from api.models import TaskType
from api.models import TaskList
from api.models import AddIns
from api.models import DelIns
from api.models import SnapIns
from api.models import SettingIns
from api.models import CtrlIns
from api.models import AddVmFile
from api.models import SetNetIns


class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'age', 'failed', )
    search_fields = ('type', 'name', 'age', 'failed', )  # 搜索字段
    list_filter = ('name', )  # 过滤器


class TaskListAdmin(admin.ModelAdmin):
    list_display = ('server', 'instance', 'status', 'type',)
    search_fields = ('server', 'instance', 'type', 'status', 'group_id')  # 搜索字段
    list_filter = ('server', 'instance', 'type', 'status', 'group_id')  # 过滤器


class AddInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'vm_name', 'vm_file', 'cpu_num', 'mem_size', 'sys_disk_size', 'data_disk_size', )
    search_fields = ('vm_name', )  # 搜索字段
    list_filter = ('vm_file', )  # 过滤器


class DelInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'del_disk', )
    search_fields = ('uuid', 'del_disk', )  # 搜索字段
    list_filter = ('del_disk', )  # 过滤器


class SnapInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'snap_name',)
    search_fields = ('uuid', 'snap_name', )  # 搜索字段
    list_filter = ('snap_name', )  # 过滤器


class SettingInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'new_cpu_num', 'sysdisk_extend', 'datadisk_extend', 'new_mem_size', )
    search_fields = ('uuid', 'new_cpu_num', 'sysdisk_extend', 'datadisk_extend', 'new_mem_size', )


class CtrlInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'action', )
    search_fields = ('uuid', 'action', )  # 搜索字段
    list_filter = ('action', )  # 过滤器


class AddVmFileAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'uri', 'save_path', 'format', )
    search_fields = ('uuid', 'uri', 'save_path', 'format',)  # 搜索字段
    list_filter = ('format', )  # 过滤器


class SetNetInsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'nic_name', 'ip', 'bootproto', 'netmask', 'gateway', 'dns',)
    search_fields = ('uuid', 'nic_name', 'ip', 'bootproto', 'netmask', 'gateway', 'dns',)  # 搜索字段
    list_filter = ('bootproto',)  # 过滤器


admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(TaskList, TaskListAdmin)
admin.site.register(AddIns, AddInsAdmin)
admin.site.register(DelIns, DelInsAdmin)
admin.site.register(SnapIns, SnapInsAdmin)
admin.site.register(SettingIns, SettingInsAdmin)
admin.site.register(CtrlIns, CtrlInsAdmin)
admin.site.register(AddVmFile, AddVmFileAdmin)
admin.site.register(SetNetIns, SetNetInsAdmin)
