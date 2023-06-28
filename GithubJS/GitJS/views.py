from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Project, Branch


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class ProjectView(generic.DetailView):
    model = Project
    template_name = "project_view.html"


def single_branch(request, project_id, branch_id):
    project = get_object_or_404(Project, id=project_id)
    branch = get_object_or_404(Branch, id=branch_id)
    if branch.project.id != project_id:
        raise Http404("Branch doesn't match the project")
    return render(request, 'branch_view.html', {"name": branch.name, "project": project})


def add_branch(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "branch_form.html", {"project": project})
    else:
        new_branch_name = request.POST['new_branch']
        if new_branch_name.strip() == '':
            error_message = "Branch name can't be empty"
            return render(request, "branch_form.html", {"project": project, "error_message": error_message})
        b = Branch(name=new_branch_name)
        b.project = project
        b.save()
        return HttpResponseRedirect(reverse("single_project", args=(project.id,)))
