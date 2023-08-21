from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .models import Project, Comment, GitUser, Reaction, PullRequest, Issue, Branch


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "project_view.html", {"project": project, "title": project.title,
                                                     'comments': project.get_comments(request.user.username)})
    else:
        new_comment = request.POST['new_comment'].strip()
        error_message = ''
        if new_comment == '':
            error_message = "You can't submit an empty comment"
        if error_message:
            return render(request, "project_view.html", {"project": project, "title": project.title,
                                                         "error_message": error_message,
                                                         'comments': project.get_comments(request.user.username)})

        new_id = len(Comment.objects.all())+1
        comment = Comment(id=new_id, text=new_comment, last_update=timezone.now())
        comment.project = project
        comment.user = GitUser.objects.get_by_natural_key(request.user.username)
        comment.project.update_users('Comment added in ' + project.title + ' by ' + request.user.username)
        comment.save()
        return render(request, "project_view.html", {"project": project, "title": project.title,
                                                     'comments': comment.project.get_comments(request.user.username)})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def toggle_reaction(request, comment_id, reaction_type):
    comment = get_object_or_404(Comment, id=comment_id)
    user = get_object_or_404(GitUser, id=request.user.pk)
    reaction = Reaction.objects.filter(comment=comment, user=user)
    if len(reaction) == 0:
        new_id = Reaction.objects.all().order_by('-id')[0].id + 1
        new_reaction = Reaction(id=new_id, user=user, comment=comment, type=reaction_type)
        comment.project.update_users('Reaction added for comment ' + str(comment_id) + ' by ' + request.user.username)
        new_reaction.save()
        return render(request, "project_view.html", {"project": comment.project, "title": comment.project.title,
                                                     'comments': comment.project.get_comments(request.user.username)})
    else:
        existing_reaction = reaction[0]
        if existing_reaction.type == reaction_type:
            comment.project.update_users('Reaction deleted for comment ' + str(comment_id) +
                                         ' by ' + request.user.username)
            existing_reaction.delete()
        else:
            existing_reaction.type = reaction_type
            comment.project.update_users('Reaction changed for comment in ' + str(comment_id) + ' by '
                                         + request.user.username)
            existing_reaction.save()
        return render(request, "project_view.html", {"project": comment.project, "title": comment.project.title,
                                                     'comments': comment.project.get_comments(request.user.username)})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def view_pull_requests(request, project_id, state):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'pull_requests.html', {'title': 'Pull requests for ' + project.title,
                                                  'project_id': project_id,
                                                  'pull_requests': project.get_pull_requests(state)})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_pull_request(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "pr_form.html", {"title": "New pull request", "input_title": "",
                                                "input_desc": "", "source_branch": "", "target_branch": "",
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

        if error_message:
            return render(request, "pr_form.html", {"error_message": error_message, 'input_issue': '',
                                                    "title": "New pull request", "input_title": "",
                                                    "input_desc": "", "source_branch": "", "target_branch": "",
                                                    'branches': project.get_branches(),
                                                    'issues': project.get_issues('OPEN'),
                                                    'form_action': str(project_id)+'/add_pull_request'})

        existing_pr = PullRequest.objects.filter(project=project, title=new_title)
        if len(existing_pr) > 0:
            error_message = 'Pull request with given title already exists'
            return render(request, "pr_form.html", {"error_message": error_message, 'input_issue': '',
                                                    "title": "New pull request", "input_title": "",
                                                    "input_desc": "", "source_branch": "", "target_branch": "",
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

        return HttpResponseRedirect(reverse("pull_requests", args=(project_id, 'OPEN', )))