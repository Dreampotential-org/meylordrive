from django.db import models
from django.contrib.auth import get_user_model


class Org(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    name = models.CharField(max_length=4096, blank=True, null=True)

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
    hypervisor_vendor = models.CharField(max_length=100, blank=True, null=True)
    virtualization_type = models.CharField(max_length=100,
                                           blank=True, null=True)
    l1d_cache = models.CharField(max_length=100)
    l1i_cache = models.CharField(max_length=100)
    l2_cache = models.CharField(max_length=100)
    l3_cache = models.CharField(max_length=100)
    total_memory = models.IntegerField(blank=True, null=True)

    def ___str__(self):
        return str(self.model_name)


class Server(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
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

    def __str__(self):
        return str(self.name)


class KeyPair(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    value = models.TextField()

    def __str__(self):
        return str(self.user)


class ServerUserKey(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    server = models.ForeignKey(Server, on_delete=models.CASCADE,
                               blank=True, null=True, default=None)
    keypair = models.ForeignKey(KeyPair, on_delete=models.CASCADE,
                                blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.user},  {self.server},  {self.keypair}"


class ServerGroup(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(get_user_model())
    servers = models.ManyToManyField(Server)

    def __str__(self):
        return str(self.name)


class ProjectMember(models.Model):
    added_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None,
                            related_name="added_by")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    admin = models.BooleanField(default=False)
    role = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    org = models.ForeignKey(Org, on_delete=models.CASCADE,
                            null=True, blank=True, default=None)


class ProjectCommand(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    cmd = models.CharField(max_length=4096, blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_started_at = models.DateTimeField(blank=True, null=True)
    last_finished_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=4096, null=True, blank=True)
    meta = models.TextField(null=True, blank=True)
    description = models.TextField(blank=True, null=True, default="")
    environment_variable = models.JSONField(blank=True, null=True,
                                            default=dict)

    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    repo = models.CharField(max_length=4096, null=True, blank=True)
    # can create public private projects


class ProjectService(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    repo = models.CharField(max_length=4096, null=True, blank=True)
    command = models.ForeignKey(ProjectCommand, on_delete=models.CASCADE,
                                null=True, blank=True)
    name = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=64, blank=True, null=True)

    server_group = models.ForeignKey(ServerGroup, on_delete=models.CASCADE,
                                    blank=True, null=True)


class Domain(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             null=True, blank=True, default=None)
    name = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    project_service = models.ForeignKey(
        ProjectService, on_delete=models.CASCADE,
        blank=True, null=True)


class ProjectServiceLog(models.Model):
    project_service = models.ForeignKey(ProjectService,
                                        on_delete=models.CASCADE,)
    stdout = models.TextField(blank=True, null=True)
    file_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

