from django.http import HttpResponse
from django.shortcuts import render

from .models import Project, Branch


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def single_project(request, project_id):
    project = Project.objects.get(id=project_id)
    return render(request, 'project_view.html', {"project": project})


def single_branch(request, project_id, branch_id):
    project = Project.objects.get(id=project_id)
    branch = Branch.objects.get(id=branch_id)
    return render(request, 'branch_view.html', {"name": branch.name, "project": project})
