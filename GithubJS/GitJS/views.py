from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
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


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_view.html', {'title': project.title, "project": project})


def single_branch(request, project_id, branch_id):
    project = get_object_or_404(Project, id=project_id)
    branch = get_object_or_404(Branch, id=branch_id)
    if branch.project.id != project_id:
        raise Http404("Branch doesn't match the project")
    return render(request, 'branch_view.html', {"name": branch.name, "project": project, "title": "Single branch"})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
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


def git_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'GET':
        return render(request, "login.html", {"title": "Index"})
    elif request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['psw']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            # neuspesno
            return render(request, "login.html", {"title": "Login greska!", 'greska_login': True})
    else:
        raise Http404()


def git_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index')
    raise PermissionDenied()
