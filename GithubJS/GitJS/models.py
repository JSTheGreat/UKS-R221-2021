from django.db import models
from django.contrib.auth.models import User


class GitUser(User):
    pass


class Project(models.Model):
    title = models.CharField(max_length=100)
    lead = models.ForeignKey(GitUser, on_delete=models.CASCADE)

    def get_branch_number(self):
        branches = Branch.objects.filter(project=self)
        return len(branches)


class Branch(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
