import datetime

from django.utils import timezone
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Branch, GitUser, Issue, Milestone


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def get_issues(request, project_id, state):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    return render(request, 'issues.html', {'title': 'Issues for ' + project.title, 'project_id': project_id,
                                           'issues': project.get_issues(state), 'can_edit': can_edit})
