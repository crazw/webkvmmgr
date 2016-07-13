# coding=utf-8
from __future__ import unicode_literals
from django.db import models


# 设备清单
class Server(models.Model):
    # 前端配置或计算的
    name = models.CharField(max_length=45, default='未知', verbose_name='单位名称')
    alias = models.CharField(max_length=45, default='未知', verbose_name='设备别名')
    islock = models.IntegerField(default=1, verbose_name='锁定状态',
                                 help_text="0:锁定；1:解锁")

    # 主机硬件配置（host.hw）
    architecture = models.CharField(max_length=10, default='未知', verbose_name='系统位数')
    version = models.CharField(max_length=10, default='0.0.0', verbose_name='业务包版本')
    libvirt_version = models.CharField(max_length=10, default='0.0.0', verbose_name='libvirt版本')
    hv_version = models.CharField(max_length=10, default='0.0.0', verbose_name='hypervisor版本')
    cpu_name = models.CharField(max_length=100, default='未知', verbose_name='CPU名称')
    cpu_num = models.IntegerField(default=0, verbose_name='CPU(核)')
    mem_size = models.BigIntegerField(blank=False, default=0, verbose_name='内存总数(Byte)')
    disk_size = models.BigIntegerField(blank=False, default=0, verbose_name='磁盘大小(Byte)')
    data_disk_num = models.IntegerField(blank=False, default=0, verbose_name='数据盘数量(个)')

    # 主机状态 (host.status)
    sn = models.CharField(max_length=13, verbose_name='sn')
    refresh = models.DateTimeField(blank=False, null=True, verbose_name='刷新时间',
                                   help_text="用于判断设备是否失联，根据设备的host_status反馈来更新")
    ip = models.GenericIPAddressField(max_length=15, default='0.0.0.0', verbose_name='出口IP')
    status = models.IntegerField(default=0, verbose_name='状态',
                                 help_text='(1--在线; 0--关机;  2--前端显示(失联),刷新时间超过一小时)')

    class Meta:
        verbose_name = '设备清单'
        verbose_name_plural = '1-设备列表'

    def __unicode__(self):
        return u'%s' % self.sn


# --------- 配置相关
# 设备VM Files表
class VmFile(models.Model):
    server = models.ForeignKey('Server', related_name='vf_server', verbose_name='VM File的关联设备')
    name = models.CharField(max_length=100, verbose_name='VM镜像名称')
    size = models.BigIntegerField(default=0, verbose_name='镜像大小',
                                  help_text='单位: byte')
    format = models.IntegerField(verbose_name='镜像类型',
                                 help_text='说明: 0--iso；1--qcow2; 2--未知;')
    source = models.IntegerField(verbose_name='镜像文件来源',
                                 help_text='说明: 0--设备预装 or FTP添加并下载完成； 1--FTP添加未下载； 2--未知;')
    path = models.CharField(verbose_name='镜像保存路经', max_length=50,
                            help_text='一般是服务端配置的模板路径和镜像路径')
    comment = models.TextField(verbose_name='备注信息')

    class Meta:
        verbose_name = '设备VM Files表'
        verbose_name_plural = '2-设备VM Files表'

    def __unicode__(self):
        return u'%s' % self.name


# 设备镜像配置模板表
class IosTemplate(models.Model):
    server = models.ForeignKey('Server', related_name='it_server', verbose_name='镜像模板的关联设备')
    name = models.CharField(max_length=100, verbose_name='VM模板镜像名称')
    vm_file = models.ForeignKey('VmFile', related_name='vm_files', verbose_name='关联VmFile')
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
    comment = models.TextField(verbose_name='备注信息')

    class Meta:
        verbose_name = '设备镜像配置模板表'
        verbose_name_plural = '3-设备镜像配置模板表'

    def __unicode__(self):
        return u'%s' % self.name


# 磁盘配置
class SDiskConf(models.Model):
    server = models.ForeignKey('Server', related_name='sdc_server', verbose_name='磁盘配置的关联设备')
    create_time = models.DateTimeField(verbose_name='创建时间',
                                       help_text='该配置创建的时间')
    refresh = models.DateTimeField(verbose_name='创建时间',
                                   help_text='目的是确定该配置失效的时间')
    source = models.CharField(max_length=100, verbose_name='源数据盘')
    total_size = models.BigIntegerField(default=0, verbose_name='总大小',
                                        help_text='单位: Byte')
    mounted = models.CharField(max_length=100, verbose_name='挂载路径')

    class Meta:
        verbose_name = '设备磁盘配置'
        verbose_name_plural = '4-设备设备磁盘配置'

    def __unicode__(self):
        return u'%s | %s' % (self.source, self.mounted)


# 网卡配置
class SNetConf(models.Model):
    server = models.ForeignKey('Server', related_name='snc_server', verbose_name='网卡配置的关联设备')
    create_time = models.DateTimeField(verbose_name='创建时间',
                                       help_text='该配置创建的时间')
    refresh = models.DateTimeField(verbose_name='创建时间',
                                   help_text='目的是确定该配置失效的时间')
    name = models.CharField(verbose_name='网卡名称', max_length=30)
    net_type = models.CharField(verbose_name='网卡类型', max_length=20,
                                help_text='说明: monitor-镜像网卡； server-服务网卡')

    class Meta:
        verbose_name = '设备网卡配置'
        verbose_name_plural = '5-设备网卡配置'

    def __unicode__(self):
        return u'%s | %s' % (self.name, self.net_type)


# ------- 状态相关
# 设备基础状态信息表
class SBasicStat(models.Model):
    server = models.ForeignKey('Server', related_name='sbs_server', verbose_name='基础状态的关联设备')
    create_time = models.DateTimeField(verbose_name='时间')
    stat_type = models.CharField(verbose_name='状态类型', max_length=10,
                                 help_text='选项，cpu_used, disk_used, mem_used')
    value = models.FloatField(default=0, verbose_name='百分比',
                              help_text='保留两位小数')

    class Meta:
        verbose_name = '基础状态信息表'
        verbose_name_plural = '6-基础状态信息表'

    def __unicode__(self):
        return u'%s' % self.stat_type


# 设备磁盘状态详情表
class SDiskStat(models.Model):
    disk_name = models.ForeignKey('SDiskConf', related_name='sds_disk', verbose_name='关联的磁盘配置')
    create_time = models.DateTimeField(verbose_name='时间',
                                       help_text='数值和DiskConf里refresh一致')
    used = models.FloatField(default=0, verbose_name='使用率',
                             help_text='保留两位小数')
    util = models.FloatField(default=0, verbose_name='磁盘Util',
                             help_text='保留两位小数')

    class Meta:
        verbose_name = '磁盘状态详情表'
        verbose_name_plural = '7-磁盘状态详情表'

    def __unicode__(self):
        return u'%s | %s' % (self.used, self.util)


# 设备网络状态详情表
class SNetStat(models.Model):
    net_name = models.ForeignKey('SNetConf', related_name='sns_net', verbose_name='关联的网络配置')
    create_time = models.DateTimeField(verbose_name='时间',
                                       help_text='数值和DiskConf里refresh一致')
    net_in = models.BigIntegerField(default=0, verbose_name='入口流量',
                                    help_text='单位: KBps')
    net_out = models.BigIntegerField(default=0, verbose_name='出口流量',
                                     help_text='单位: KBps')

    class Meta:
        verbose_name = '网络状态详情表'
        verbose_name_plural = '8-网络状态详情表'

    def __unicode__(self):
        return u'%s | %s' % (self.net_in, self.net_out)
