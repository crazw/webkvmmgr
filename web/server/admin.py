# coding=utf-8
from django.contrib import admin
from server.models import Server
from server.models import VmFile
from server.models import IosTemplate
from server.models import SDiskConf
from server.models import SNetConf
from server.models import SBasicStat
from server.models import SDiskStat
from server.models import SNetStat


# Register your models here.
class ServerAdmin(admin.ModelAdmin):
    list_display = ('sn', 'name', 'alias', 'status', 'refresh', )
    search_fields = ('sn', 'islock', 'hv_version', 'libvirt_version', 'status', )  # 搜索字段
    list_filter = ('sn', 'islock', 'hv_version', 'libvirt_version', 'status', )  # 过滤器


class VmFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'size', 'format', 'source', )
    search_fields = ('server', 'name', 'format', 'source', )  # 搜索字段
    list_filter = ('server', 'format', 'source', )  # 过滤器


class IosTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'vm_file', 'comment',)
    search_fields = ('server', 'name', 'vm_file',)  # 搜索字段
    list_filter = ('server', 'vm_file',)  # 过滤器


class SDiskConfAdmin(admin.ModelAdmin):
    list_display = ('server', 'source', 'mounted', 'create_time', 'refresh', )
    search_fields = ('server', )  # 搜索字段
    list_filter = ('server', )  # 过滤器


class SNetConfAdmin(admin.ModelAdmin):
    list_display = ('name', 'server', 'create_time', 'refresh', )
    search_fields = ('name', 'server', 'create_time', 'refresh', )  # 搜索字段
    list_filter = ('name', 'server', )  # 过滤器


class SBasicStatAdmin(admin.ModelAdmin):
    list_display = ('stat_type', 'server', 'value', 'create_time', )
    search_fields = ('stat_type', 'server', )  # 搜索字段
    list_filter = ('stat_type', 'server', )  # 过滤器


class SDiskStatAdmin(admin.ModelAdmin):
    list_display = ('disk_name', 'used', 'util', 'create_time',)
    search_fields = ('disk_name', )  # 搜索字段
    list_filter = ('disk_name', )  # 过滤器


class SNetStatAdmin(admin.ModelAdmin):
    list_display = ('net_name', 'net_in', 'net_out', 'create_time', )
    search_fields = ('net_name', )  # 搜索字段
    list_filter = ('net_name', )  # 过滤器


admin.site.register(Server, ServerAdmin)
admin.site.register(VmFile, VmFileAdmin)
admin.site.register(IosTemplate, IosTemplateAdmin)
admin.site.register(SDiskConf, SDiskConfAdmin)
admin.site.register(SNetConf, SNetConfAdmin)
admin.site.register(SBasicStat, SBasicStatAdmin)
admin.site.register(SDiskStat, SDiskStatAdmin)
admin.site.register(SNetStat, SNetStatAdmin)
