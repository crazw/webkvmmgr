# coding=utf-8
from __future__ import unicode_literals
from django.db import models
import uuid


# 任务类型
class TaskType(models.Model):
    name = models.CharField(max_length=100, verbose_name='任务名称')
    type = models.IntegerField(blank=False, default=0, verbose_name='任务类型号',
                               help_text="说明: 1-新建虚拟机;2-更新虚拟机配置;3-删除虚拟机;"
                                         "4-虚拟机创建快照;5-虚拟机恢复快照;7-删除快照;"
                                         "8-网卡配置;20-启动/停止虚拟机;40--下载任务;")
    age = models.IntegerField(blank=False, default=0, verbose_name='领取有效期(秒)')
    failed = models.IntegerField(blank=False, default=0, verbose_name='响应有效期(秒)',
                                 help_text="提示: 1分钟: 60; 5分钟: 300; 10分钟: 600; 半小时: 1800;")

    class Meta:
        verbose_name = '任务有效期'
        verbose_name_plural = '1-任务类型注册'

    def __unicode__(self):
        return u'%s | %s' % (self.type, self.name)


class TaskList(models.Model):
    server = models.ForeignKey('server.Server', related_name='task_server', verbose_name='任务的关联设备')
    instance = models.ForeignKey('instance.Instance', related_name='task_instance', null=True, blank=True,
                                 verbose_name='任务的关联虚拟机', help_text='当没有虚拟机可关联时，值为None')
    type = models.ForeignKey('TaskType', related_name='task_type', verbose_name='任务的关联类型')
    create_time = models.CharField(verbose_name='创建时间', default='2016-01-01 00:00:00',
                                   max_length=20, help_text='创建时插入当前时间')

    end_time = models.CharField(verbose_name='完成时间', default='2016-01-01 00:00:00',
                                max_length=20, help_text='创建时插入当前时间')
    uuid = models.UUIDField(verbose_name='UUID', primary_key=True, default=uuid.uuid4, editable=False)
    group_id = models.CharField(verbose_name='任务组ID', max_length=32, null=True, default=None)
    father_id = models.CharField(verbose_name='父任务ID', max_length=32, null=True, default=None)

    status = models.IntegerField(default=0, verbose_name='任务状态',
                                 help_text='0-创建未发布, 1-发布未领取, 2-领取未完成, 3-完成且成功, 4-完成却失败, 5-取消')

    class Meta:
        verbose_name = '所有任务清单'
        verbose_name_plural = '2-所有任务清单'

    def __unicode__(self):
        return u'%s | %s' % (self.instance, self.type)


class AddIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='ai_uuid', verbose_name='任务的关联UUID')
    vm_name = models.CharField(verbose_name='虚拟机名称', max_length=30)
    vm_file = models.ForeignKey('server.VmFile', related_name='ai_vmfiles', verbose_name='关联VmFile')
    cpu_num = models.IntegerField(default=0, verbose_name='CPU(核)')
    cpu_model = models.IntegerField(default=1, verbose_name='CPU模式',
                                    help_text='此功能暂时未实现（配方），全部默认为1')
    disk_model = models.IntegerField(default=1, verbose_name='数据盘模式',
                                     help_text='此功能暂时未实现（配方），全部默认为1')
    sys_disk_size = models.BigIntegerField(default=0, verbose_name='系统盘大小',
                                           help_text='单位: Byte')
    data_disk_size = models.BigIntegerField(default=0, verbose_name='数据盘盘大小',
                                            help_text='单位: Byte')
    mem_size = models.BigIntegerField(default=0, verbose_name='内存大小',
                                      help_text='单位: Byte')

    class Meta:
        verbose_name = '创建虚拟机'
        verbose_name_plural = '3-创建虚拟机'

    def __unicode__(self):
        return u'%s | %s' % (self.vm_name, self.uuid)


class DelIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='di_uuid', verbose_name='任务的关联UUID')
    del_disk = models.IntegerField(default=0, verbose_name='删除数据盘',
                                   help_text='0-删除, 1-不删除')

    class Meta:
        verbose_name = '删除虚拟机'
        verbose_name_plural = '4-删除虚拟机'

    def __unicode__(self):
        return u'%s | %s' % (self.uuid, self.del_disk)


class SnapIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='si_uuid', verbose_name='任务的关联UUID')
    snap_name = models.CharField(verbose_name='快照名称', max_length=50)

    class Meta:
        verbose_name = '快照相关操作'
        verbose_name_plural = '5-快照相关操作'

    def __unicode__(self):
        return u'%s | %s' % (self.uuid, self.snap_name)


class SettingIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='si2_uuid', verbose_name='任务的关联UUID')
    new_cpu_num = models.IntegerField(verbose_name='新CPU配置(核)')
    sysdisk_extend = models.BigIntegerField(default=0, verbose_name='新增系统盘大小',
                                            help_text='单位: Byte')
    datadisk_extend = models.BigIntegerField(default=0, verbose_name='新增数据盘盘大小',
                                             help_text='单位: Byte')
    new_mem_size = models.BigIntegerField(default=0, verbose_name='新内存大小',
                                          help_text='单位: Byte')

    class Meta:
        verbose_name = '虚拟机增加配置'
        verbose_name_plural = '6-虚拟机增加配置'

    def __unicode__(self):
        return u'%s' % self.uuid


class CtrlIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='ci_uuid', verbose_name='任务的关联UUID')
    action = models.CharField(verbose_name='操作', max_length=10)

    class Meta:
        verbose_name = '虚拟机开关机'
        verbose_name_plural = '7-虚拟机开关机'

    def __unicode__(self):
        return u'%s | %s' % (self.uuid, self.action)


class AddVmFile(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='avf_uuid', verbose_name='任务的关联UUID')

    uri = models.CharField(max_length=1000, default='', verbose_name='下载地址')
    size = models.IntegerField(blank=False, default=0, verbose_name='文件大小')
    md5 = models.CharField(max_length=45, default='', verbose_name='MD5')
    save_path = models.CharField(max_length=45, default='', verbose_name='保存路径')
    format = models.IntegerField(blank=False, default=0, verbose_name='文件类型',
                                 help_text='0-iso, 1-qcow2, 3-未知 ')

    class Meta:
        verbose_name = '添加镜像文件'
        verbose_name_plural = '8-添加镜像文件'

    def __unicode__(self):
        return u'%s | %s | %s' % (self.uuid, self.md5, self.format)


class SetNetIns(models.Model):
    uuid = models.ForeignKey('TaskList', related_name='sni_uuid', verbose_name='任务的关联UUID')
    nic_name = models.CharField(max_length=45, verbose_name='网卡名称')
    ip = models.CharField(max_length=45, default='', verbose_name='绑定IP')
    bootproto = models.CharField(max_length=45, default='', verbose_name='类型')
    netmask = models.CharField(max_length=45, default='', verbose_name='子网掩码')
    gateway = models.CharField(max_length=45, default='', verbose_name='网关')
    dns = models.CharField(max_length=45, default='', verbose_name='DNS')

    class Meta:
        verbose_name = '配置网卡'
        verbose_name_plural = '9-配置网卡'

    def __unicode__(self):
        return u'%s | %s | %s | %s' % (self.uuid, self.ip, self.nic_name, self.bootproto)
