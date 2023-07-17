from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from .models import Project, Branch, GitUser, StarredProject

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import redis


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def single_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        starred = StarredProject.objects.get(project_id=project_id, user_id=request.user.pk)
        return render(request, 'project_view.html', {'title': project.title, "project": project, "starred": True})
    except:
        return render(request, 'project_view.html', {'title': project.title, "project": project, "starred": False})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def starred_projects(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'projects.html', {'title': 'Starred projects', 'projects': user.get_starred_projects()})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_starred(request, project_id):
    user = get_object_or_404(GitUser, id=request.user.pk)
    user.add_starred(project_id)
    return redirect('index')


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def remove_starred(request, project_id):
    user = get_object_or_404(GitUser, id=request.user.pk)
    user.remove_starred(project_id)
    return redirect('index')
