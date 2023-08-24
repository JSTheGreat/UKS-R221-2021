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
def get_milestone_issues(request, milestone_id, state):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    can_edit = milestone.project.can_edit(request.user.username)
    return render(request, 'issues.html', {'title': 'Issues for ' + milestone.title, 'milestone_id': milestone.id,
                                           'issues': milestone.get_issues(state), 'can_edit': can_edit,
                                           'project': milestone.project})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
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
        issue.project.update_users('New issue added in ' + project.title)
        return HttpResponseRedirect(reverse("issues", args=(project_id, 'OPEN', )))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def edit_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    old_assignee = issue.assignee.username if issue.assignee else 'None'
    old_milestone = issue.milestone.title if issue.milestone else 'None'
    if request.method == 'GET':
        return render(request, 'issue_form.html', {'title': 'Issue #'+str(issue_id), 'project_id': issue.project.id,
                                                   'form_action': 'edit_issue/' + str(issue_id),
                                                   'input_title': issue.title, 'input_desc': issue.description,
                                                   'input_assignee': old_assignee,
                                                   'input_milestone': old_milestone,
                                                   'milestones': issue.project.get_milestones('OPEN'),
                                                   'participants': issue.project.get_all_participants()
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
            return render(request, 'issue_form.html', {'title': 'Issue #'+str(issue_id), 'project_id': issue.project.id,
                                                       'form_action': 'edit_issue/' + str(issue_id),
                                                       'input_title': issue.title, 'input_desc': issue.description,
                                                       'input_assignee': old_assignee,
                                                       'input_milestone': old_milestone,
                                                       'milestones': issue.project.get_milestones('OPEN'),
                                                       'participants': issue.project.get_all_participants(),
                                                       'error_message': error_message,
                                                       })
        existing_issues = Issue.objects.filter(title=new_title)
        if len(existing_issues) != 0 and existing_issues[0].id != issue_id:
            error_message = 'Issue with given title already exists'
            return render(request, 'issue_form.html', {'title': 'Issue #'+str(issue_id), 'project_id': issue.project.id,
                                                       'form_action': 'edit_issue/' + str(issue_id),
                                                       'input_title': issue.title, 'input_desc': issue.description,
                                                       'input_assignee': old_assignee,
                                                       'input_milestone': old_milestone,
                                                       'milestones': issue.project.get_milestones('OPEN'),
                                                       'participants': issue.project.get_all_participants(),
                                                       'error_message': error_message,
                                                       })
        issue.project.update_users('Issue ' + issue.title + ' updated in ' + issue.project.title)
        issue.title = new_title
        issue.description = new_desc
        if milestone != 'None':
            issue.milestone = Milestone.objects.get(title=milestone)
        else:
            issue.milestone = None
        if assignee != 'None':
            issue.assignee = GitUser.objects.get_by_natural_key(assignee)
        else:
            issue.assignee = None
        issue.save()

        return HttpResponseRedirect(reverse("issues", args=(issue.project.id, 'OPEN', )))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def toggle_issue_status(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    if issue.state == 'OPEN':
        issue.state = 'CLOSED'
        issue.project.update_users('Issue ' + issue.title + ' closed in ' + issue.project.title)
    else:
        issue.state = 'OPEN'
        issue.project.update_users('Issue ' + issue.title + ' opened in ' + issue.project.title)
    issue.save()
    return HttpResponseRedirect(reverse("issues", args=(issue.project.id, 'OPEN',)))
