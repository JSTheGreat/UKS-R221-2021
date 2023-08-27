from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .models import Project, PullRequest, Issue, Branch, Commit


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def view_pull_requests(request, project_id, state):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    return render(request, 'pull_requests.html', {'title': 'Pull requests for ' + project.title,
                                                  'project_id': project_id, 'can_edit': can_edit,
                                                  'pull_requests': project.get_pull_requests(state)})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_pull_request(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    if len(Branch.objects.filter(project=project, default=True)) > 0:
        default_branch_name = Branch.objects.filter(project=project, default=True)[0].name
    else:
        default_branch_name = ''
    if request.method == 'GET':
        return render(request, "pr_form.html", {"title": "New pull request", "input_title": "",
                                                'project_id': project.id, 'can_edit': can_edit,
                                                "input_desc": "", "source_branch": "",
                                                "target_branch": default_branch_name,
                                                'input_issue': '',
                                                'branches': project.get_branches(),
                                                'issues': project.get_issues('OPEN'),
                                                'form_action': str(project_id)+'/add_pull_request'})
    else:
        new_title = request.POST['new_title'].strip()
        new_desc = request.POST['new_desc'].strip()
        new_issue = request.POST['new_issue']
        source_branch = request.POST['source_branch']
        target_branch = request.POST['target_branch']

        error_message = ''
        if new_title == '':
            error_message = "Title can't be empty"
        elif source_branch == '':
            error_message = "Source branch must be chosen"
        elif target_branch == '':
            error_message = "Target branch must be chosen"
        elif target_branch == source_branch:
            error_message = "Source and target branch can't be the same"

        if error_message:
            return render(request, "pr_form.html", {"error_message": error_message, 'input_issue': '',
                                                    'project_id': project.id, 'can_edit': can_edit,
                                                    "title": "New pull request", 'input_title': '',
                                                    "input_desc": "", "source_branch": "",
                                                    "target_branch": default_branch_name,
                                                    'branches': project.get_branches(),
                                                    'issues': project.get_issues('OPEN'),
                                                    'form_action': str(project_id)+'/add_pull_request'})

        existing_pr = PullRequest.objects.filter(project=project, title=new_title)
        if len(existing_pr) > 0:
            error_message = 'Pull request with given title already exists'
            return render(request, "pr_form.html", {"error_message": error_message, 'input_issue': '',
                                                    'project_id': project.id, 'can_edit': can_edit,
                                                    "title": "New pull request", "input_title": "",
                                                    "input_desc": "", "source_branch": "",
                                                    "target_branch": default_branch_name,
                                                    'branches': project.get_branches(),
                                                    'issues': project.get_issues('OPEN'),
                                                    'form_action': str(project_id)+'/add_pull_request'})

        new_id = PullRequest.objects.all().order_by('-id')[0].id + 1
        new_pr = PullRequest(id=new_id, project=project, title=new_title, description=new_desc, state='OPEN')
        if new_issue != 'None':
            new_pr.issue = Issue.objects.get(title=new_issue)
        new_pr.source = Branch.objects.get(name=source_branch)
        new_pr.target = Branch.objects.get(name=target_branch)
        new_pr.save()

        new_pr.project.update_users('New pull request added!')

        return HttpResponseRedirect(reverse("pull_requests", args=(project_id, 'OPEN', )))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def edit_pull_request(request, pr_id):
    pull_request = get_object_or_404(PullRequest, id=pr_id)
    issue_title = pull_request.issue.title if pull_request.issue is not None else 'None'
    can_edit = pull_request.project.can_edit(request.user.username)
    if request.method == 'GET':
        return render(request, "pr_form.html", {"title": "Pull request #"+str(pr_id),
                                                'can_edit': can_edit,
                                                'project_id': pull_request.project.id,
                                                "input_title": pull_request.title,
                                                "input_desc": pull_request.description,
                                                "source_branch": pull_request.source.name,
                                                "target_branch": pull_request.target.name,
                                                'input_issue': issue_title,
                                                'branches': pull_request.project.get_branches(),
                                                'issues': pull_request.project.get_issues('OPEN'),
                                                'form_action': 'edit_pull_request/'+str(pr_id)})
    else:
        new_title = request.POST['new_title'].strip()
        new_desc = request.POST['new_desc'].strip()
        new_issue = request.POST['new_issue']
        source_branch = request.POST['source_branch']
        target_branch = request.POST['target_branch']

        error_message = ''
        if new_title == '':
            error_message = "Title can't be empty"
        elif source_branch == '':
            error_message = "Source branch must be chosen"
        elif target_branch == '':
            error_message = "Target branch must be chosen"
        elif target_branch == source_branch:
            error_message = "Source and target branch can't be the same"

        if error_message:
            return render(request, "pr_form.html", {"error_message": error_message,
                                                    "title": "Pull request #" + str(pr_id),
                                                    'can_edit': can_edit,
                                                    'project_id': pull_request.project.id,
                                                    "input_title": pull_request.title,
                                                    "input_desc": pull_request.description,
                                                    "source_branch": pull_request.source.name,
                                                    "target_branch": pull_request.target.name,
                                                    'input_issue': issue_title,
                                                    'branches': pull_request.project.get_branches(),
                                                    'issues': pull_request.project.get_issues('OPEN'),
                                                    'form_action': 'edit_pull_request/' + str(pr_id)})
        existing_pr = PullRequest.objects.filter(project=pull_request.project, title=new_title)
        if len(existing_pr) > 0:
            if existing_pr[0].id != pr_id:
                error_message = 'Pull request with given title already exists'
                return render(request, "pr_form.html", {"error_message": error_message,
                                                        'can_edit': can_edit,
                                                        "title": "Pull request #" + str(pr_id),
                                                        'project_id': pull_request.project.id,
                                                        "input_title": pull_request.title,
                                                        "input_desc": pull_request.description,
                                                        "source_branch": pull_request.source.name,
                                                        "target_branch": pull_request.target.name,
                                                        'input_issue': issue_title,
                                                        'branches': pull_request.project.get_branches(),
                                                        'issues': pull_request.project.get_issues('OPEN'),
                                                        'form_action': 'edit_pull_request/' + str(pr_id)})

        pull_request.project.update_users('Pull request ' + pull_request.title + ' changed!')

        if new_issue != 'None':
            pull_request.issue = Issue.objects.get(title=new_issue)
        else:
            pull_request.issue = None
        pull_request.title = new_title
        pull_request.description = new_desc
        pull_request.source = Branch.objects.get(name=source_branch)
        pull_request.target = Branch.objects.get(name=target_branch)
        pull_request.save()

        return HttpResponseRedirect(reverse("pull_requests", args=(pull_request.project.id, 'OPEN', )))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def toggle_request_state(request, pr_id):
    pull_request = get_object_or_404(PullRequest, id=pr_id)
    if pull_request.state == 'OPEN':
        pull_request.state = 'CLOSED'
    else:
        pull_request.state = 'OPEN'
    pull_request.save()
    return HttpResponseRedirect(reverse("pull_requests", args=(pull_request.project.id, 'OPEN', )))


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def get_merge_changes(request, pr_id):
    pull_request = get_object_or_404(PullRequest, id=pr_id)
    differences = pull_request.get_differences()
    return render(request, 'merge_changes.html', {'title': 'Changes for PR#'+str(pr_id),
                                                  'project_id': pull_request.project.id,
                                                  'changes': differences, 'pr_id': pr_id})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def merge_request(request, pr_id):
    pull_request = get_object_or_404(PullRequest, id=pr_id)
    pull_request.merge_branches()
    new_commit_id = Commit.objects.all().order_by('-id')[0].id + 1
    commit = Commit(id=new_commit_id, branch=pull_request.target, committer=request.user.username,
                    date_time=timezone.now())
    commit.log_message = 'Merged from ' + pull_request.source.name
    commit.save()

    issue = pull_request.issue
    if issue is not None:
        issue.state = 'CLOSED'
        issue.save()

    project_id = pull_request.project.id
    pull_request.state = 'MERGED'
    pull_request.source = None
    pull_request.target = None
    pull_request.save()
    return HttpResponseRedirect(reverse("pull_requests", args=(project_id, 'OPEN',)))