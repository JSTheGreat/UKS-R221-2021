from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Branch, GitUser, StarredProject, WatchedProject


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def get_milestones(request, project_id, state):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'milestones.html', {'title': 'Milestones for ' + project.title, 'project_id': project_id,
                                               'milestones': project.get_milestones(state)})
