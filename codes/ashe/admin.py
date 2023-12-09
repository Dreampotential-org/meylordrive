from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Session)
admin.site.register(SessionPoint)
admin.site.register(Device)
admin.site.register(Dot)
 
