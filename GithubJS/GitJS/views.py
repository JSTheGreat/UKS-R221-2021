from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Project, Branch

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import redis

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def index(request):
    return render(request, "index.html", {"title": "Index"})


@cache_page(CACHE_TTL)
def cached_initial(request):
    redis.Redis(host='uks_js_redis', port=6379)
    return render(request, "cache_test.html", {"title": "Redis test"})


class ProjectView(generic.DetailView):
    model = Project
    template_name = "project_view.html"


def single_branch(request, project_id, branch_id):
    project = get_object_or_404(Project, id=project_id)
    branch = get_object_or_404(Branch, id=branch_id)
    if branch.project.id != project_id:
        raise Http404("Branch doesn't match the project")
    return render(request, 'branch_view.html', {"name": branch.name, "project": project, "title": "Single branch"})


def add_branch(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "branch_form.html", {"project": project, "title": "Add branch"})
    else:
        new_branch_name = request.POST['new_branch']
        if new_branch_name.strip() == '':
            error_message = "Branch name can't be empty"
            return render(request, "branch_form.html", {"project": project, "error_message": error_message,
                                                        "title": "Error!"})
        new_id = len(Branch.objects.all())+1
        b = Branch(id=new_id, name=new_branch_name)
        b.project = project

        try:
            existing_branch = Branch.objects.get(name=new_branch_name, project_id=project.id)
            error_message = "Branch name already exists"
            return render(request, "branch_form.html", {"project": project, "error_message": error_message,
                                                        "title": "Error!"})
        except:
            b.save()
            return HttpResponseRedirect(reverse("single_project", args=(project.id,)))
