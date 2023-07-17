from django.db import models
from django.contrib.auth.models import User


class GitUser(User):

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


class Project(models.Model):
    title = models.CharField(max_length=100)
    lead = models.ForeignKey(GitUser, on_delete=models.CASCADE)

    def get_branch_number(self):
        branches = Branch.objects.filter(project=self)
        return len(branches)


class StarredProject(models.Model):
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class Branch(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
