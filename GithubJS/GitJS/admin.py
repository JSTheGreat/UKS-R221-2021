from django.contrib import admin

# Register your models here.
from .models import Project, Branch, StarredProject, GitUser,\
    WatchedProject, ProjectUpdate, Milestone

admin.site.register(Project)
admin.site.register(Branch)
admin.site.register(StarredProject)
admin.site.register(GitUser)
admin.site.register(WatchedProject)
admin.site.register(ProjectUpdate)
admin.site.register(Milestone)
