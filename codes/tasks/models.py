from django.db import models


class Task(models.Model):
    unique = True
    status = models.CharField(max_length=64, blank=True, null=True)
    command = models.CharField(max_length=4096, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    repo = models.CharField(max_length=4096, null=True, blank=True)


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,)
    stdout = models.TextField(blank=True, null=True)
    file_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SystemSpecs(models.Model):
    architecture = models.CharField(max_length=100)
    cpu_op_modes = models.CharField(max_length=100)
    byte_order = models.CharField(max_length=100)
    cpu_s = models.IntegerField()
    on_line_cpu_s_list = models.CharField(max_length=100)
    threads_per_core = models.CharField(max_length=100)
    cores_per_socket = models.CharField(max_length=100)
    sockets = models.CharField(max_length=100)
    numa_nodes = models.CharField(max_length=100)
    vendor_id = models.CharField(max_length=100)
    cpu_family = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    stepping = models.CharField(max_length=100)
    cpu_mhz = models.CharField(max_length=100)
    bogo_mips = models.CharField(max_length=100)
    hypervisor_vendor = models.CharField(max_length=100)
    virtualization_type = models.CharField(max_length=100,
                                           blank=True, null=True)
    l1d_cache = models.CharField(max_length=100)
    l1i_cache = models.CharField(max_length=100)
    l2_cache = models.CharField(max_length=100)
    l3_cache = models.CharField(max_length=100)
    total_memory = models.IntegerField(blank=True, null=True)


class Server(models.Model):
    system_specs = models.ForeignKey(SystemSpecs, on_delete=models.CASCADE,
                                     blank=True, null=True)
    ip_address = models.CharField(max_length=64)
    username = models.CharField(max_length=4096, blank=True, null=True)
    password = models.CharField(max_length=4096, blank=True, null=True)
    name = models.CharField(max_length=4096, blank=True, null=True)
    error = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=False)
    in_use = models.BooleanField(default=False)


class Pipeline(models.Model):
    repo = models.CharField(max_length=4096)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return str(self.repo) or ''


class PipelineServer(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE,
                                 blank=True, null=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE,
                               blank=True, null=True)

    class Meta:
        unique_together = ('pipeline', 'server')


class GithubHook(models.Model):
    error = models.BooleanField(default=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE,
                                 blank=True, null=True)

    def __str__(self):
        return self.repo or ''
