from django.db import models


class Task(models.Model):
    unique = True
    status = models.CharField(max_length=64)
    command = models.CharField(max_length=4096, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stdout = models.TextField(null=True)
    stderr = models.TextField(null=True)


class SystemSpecs(models.Model):
    architecture = models.CharField(max_length=100)
    cpu_op_modes = models.CharField(max_length=100)
    byte_order = models.CharField(max_length=100)
    # address_sizes = models.CharField(max_length=100)
    cpu_s = models.CharField(max_length=100)
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
    # frequesncy_boost = models.CharField(max_length=100)
    cpu_mhz = models.CharField(max_length=100)
    # cpu_max_mhz = models.CharField(max_length=100)
    # cpu_min_mhz = models.CharField(max_length=100)
    bogo_mips = models.CharField(max_length=100)
    hypervisor_vendor = models.CharField(max_length=100)
    virtualization_type = models.CharField(max_length=100,
                                           blank=True, null=True)
    l1d_cache = models.CharField(max_length=100)
    l1i_cache = models.CharField(max_length=100)
    l2_cache = models.CharField(max_length=100)
    l3_cache = models.CharField(max_length=100)


class Server(models.Model):
    system_specs = models.ForeignKey(SystemSpecs, on_delete=models.CASCADE,
                                     blank=True, null=True)
    ip_address = models.CharField(max_length=64)
    username = models.CharField(max_length=4096, blank=True, null=True)
    password = models.CharField(max_length=4096, blank=True, null=True)
    error = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    alive = models.BooleanField(default=False)


class Pipeline(models.Model):
    repo = models.CharField(max_length=4096)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             blank=True, null=True)


class GithubHook(models.Model):
    repo = models.CharField(max_length=4096)
    error = models.BooleanField(default=False)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE,
                                 blank=True, null=True)
