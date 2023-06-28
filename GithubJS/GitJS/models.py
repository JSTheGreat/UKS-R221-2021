from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)

    def get_branch_number(self):
        branches = Branch.objects.filter(project=self)
        return len(branches)


class Branch(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
