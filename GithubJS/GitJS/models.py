from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from enum import Enum


class GitUser(User):

    def get_my_projects(self):
        return Project.objects.filter(lead=self)

    def get_starred_projects(self):
        starred_projects = StarredProject.objects.filter(user_id=self.pk)
        starred = []
        for sp in starred_projects:
            starred.append(Project.objects.get(id=sp.project_id))
        return starred

    def add_starred(self, project_id):
        new_starred = StarredProject(project_id=project_id, user_id=self.pk)
        new_starred.save()

    def remove_starred(self, project_id):
        starred = StarredProject.objects.get(project_id=project_id, user_id=self.pk)
        starred.delete()

    def get_watched_changes(self):
        watched_projects = ProjectUpdate.objects.filter(user_id=self.pk).order_by('-up_date')
        return watched_projects

    def add_watched(self, project_id):
        new_watched = WatchedProject(project_id=project_id, user_id=self.pk)
        new_watched.save()

    def remove_watched(self, project_id):
        watched = WatchedProject.objects.get(project_id=project_id, user_id=self.pk)
        watched.delete()


class Project(models.Model):
    title = models.CharField(max_length=100)
    lead = models.ForeignKey(GitUser, on_delete=models.CASCADE)

    def get_branch_number(self):
        branches = Branch.objects.filter(project=self)
        return len(branches)

    def update_users(self, message):
        for watched in WatchedProject.objects.filter(project_id=self.id):
            new_date = timezone.now()
            update = ProjectUpdate(project_id=self.id, user_id=watched.user_id, up_date=new_date, message=message)
            update.save()

    def get_milestones(self, state):
        milestones = Milestone.objects.filter(project=self, state=state)
        return milestones


class StarredProject(models.Model):
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class WatchedProject(models.Model):
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class ProjectUpdate(models.Model):
    up_date = models.DateTimeField("date updated")
    message = models.CharField(max_length=100)
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class Branch(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Milestone(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    due_date = models.DateTimeField("due date")
    state = models.CharField(max_length=7)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
