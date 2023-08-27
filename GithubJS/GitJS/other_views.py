from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required

from .models import Project, Comment, GitUser, Reaction, PullRequest, Issue, Branch, Commit,\
    File, Milestone, StarredProject, WatchedProject


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("single_project", args=(project_id, )))
    else:
        new_comment = request.POST['new_comment'].strip()
        error_message = ''
        if new_comment == '':
            error_message = "You can't submit an empty comment"
        if error_message:
            starred = len(StarredProject.objects.filter(project_id=project_id, user_id=request.user.pk)) > 0
            watched = len(WatchedProject.objects.filter(project_id=project_id, user_id=request.user.pk)) > 0
            can_fork = project.lead.id != request.user.pk
            return render(request, "project_view.html", {"project": project, "title": project.title,
                                                         'starred': starred, 'watched': watched,
                                                         'can_fork': can_fork, 'can_edit': can_edit,
                                                         "error_message": error_message,
                                                         'comments': project.get_comments(request.user.username)})

        new_id = len(Comment.objects.all())+1
        comment = Comment(id=new_id, text=new_comment, last_update=timezone.now())
        comment.project = project
        comment.user = GitUser.objects.get_by_natural_key(request.user.username)
        comment.project.update_users('Comment added in ' + project.title + ' by ' + request.user.username)
        comment.save()
        return HttpResponseRedirect(reverse("single_project", args=(project_id, )))


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
        return HttpResponseRedirect(reverse("single_project", args=(comment.project.id, )))
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
        return HttpResponseRedirect(reverse("single_project", args=(comment.project.id, )))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def search_app(request):
    if request.method == 'GET':
        return render(request, 'search.html', {'projects_checked': True, 'branches_checked': False,
                                               'files_checked': False, 'issues_checked': False,
                                               'milestones_checked': False, 'requests_checked': False,
                                               'input_value': ''})
    else:
        include_projects = 'include_projects' in request.POST
        include_branches = 'include_branches' in request.POST
        include_files = 'include_files' in request.POST
        include_issues = 'include_issues' in request.POST
        include_milestones = 'include_milestones' in request.POST
        include_pull_requests = 'include_pull_requests' in request.POST

        search_value = request.POST['search_value'].strip()

        projects = Project.objects.filter(title__icontains=search_value) if include_projects else None
        branches = Branch.objects.filter(name__icontains=search_value) if include_branches else None
        files = File.objects.filter(title__icontains=search_value) if include_files else None
        issues = Issue.objects.filter(title__icontains=search_value, state='OPEN') if include_issues else None
        milestones = Milestone.objects.filter(title__icontains=search_value, state='OPEN') \
            if include_milestones else None
        pull_requests = PullRequest.objects.filter(title__icontains=search_value, state='OPEN') if \
            include_pull_requests else None

        return render(request, 'search.html', {'projects': projects, 'branches': branches, 'files': files,
                                               'issues': issues, 'milestones': milestones,
                                               'pull_requests': pull_requests,
                                               'projects_checked': include_projects,
                                               'branches_checked': include_branches,
                                               'files_checked': include_files, 'issues_checked': include_issues,
                                               'milestones_checked': include_milestones,
                                               'requests_checked': include_pull_requests,
                                               'input_value': search_value})
