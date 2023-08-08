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


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_issue(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, 'issue_form.html', {'title': 'New issue', 'project_id': project_id,
                                                   'form_action': str(project_id) + '/add_issue',
                                                   'input_title': '', 'input_desc': '',
                                                   'input_assignee': '', 'input_milestone': '',
                                                   'milestones': project.get_milestones('OPEN'),
                                                   'participants': project.get_all_participants()
                                                   })
    else:
        new_title = request.POST['new_title'].strip()
        new_desc = request.POST['new_desc'].strip()
        assignee = request.POST['assignee'].strip()
        milestone = request.POST['milestone'].strip()

        error_message = ''
        if new_title == '' or new_title is None:
            error_message = 'Title can\'t be empty'
        if error_message:
            return render(request, 'issue_form.html', {'title': 'New issue', 'error_message': error_message,
                                                       'form_action': str(project_id) + '/add_issue',
                                                       'input_title': '', 'input_desc': '',
                                                       'input_assignee': '', 'input_milestone': '',
                                                       'milestones': project.get_milestones('OPEN'),
                                                       'participants': project.get_all_participants(),
                                                       'project_id': project_id
                                                       })
        existing_issues = Issue.objects.filter(title=new_title)
        if len(existing_issues) != 0:
            error_message = 'Issue with given title already exists'
            return render(request, 'issue_form.html', {'title': 'New issue', 'error_message': error_message,
                                                       'form_action': str(project_id) + '/add_issue',
                                                       'input_title': '', 'input_desc': '',
                                                       'input_assignee': '', 'input_milestone': '',
                                                       'milestones': project.get_milestones('OPEN'),
                                                       'participants': project.get_all_participants(),
                                                       'project_id': project_id
                                                       })
        new_id = Issue.objects.all().order_by('-id')[0].id + 1
        issue = Issue(id=new_id, title=new_title, description=new_desc, project=project, state='OPEN')
        if milestone != 'None':
            issue.milestone = Milestone.objects.get(title=milestone)
        if assignee != 'None':
            issue.assignee = GitUser.objects.get_by_natural_key(assignee)
        issue.save()

        return HttpResponseRedirect(reverse("issues", args=(project_id, 'OPEN', )))
