from django.contrib import admin

# Register your models here.
from .models import Project, Branch

admin.site.register(Project)
admin.site.register(Branch)
