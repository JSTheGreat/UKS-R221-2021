from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Branch, GitUser, StarredProject, WatchedProject, Contributor


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def single_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(GitUser, id=request.user.pk)
    can_fork = project.lead.id != user.id
    can_edit = project.can_edit(user.username)
    try:
        starred = StarredProject.objects.get(project_id=project_id, user_id=request.user.pk)
        try:
            watched = WatchedProject.objects.get(project_id=project_id, user_id=request.user.pk)
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": True, "watched": True, "can_fork": can_fork,
                                                         'comments': project.get_comments(user.username),
                                                         'can_edit': can_edit})
        except:
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": True, "watched": False, "can_fork": can_fork,
                                                         'comments': project.get_comments(user.username),
                                                         'can_edit': can_edit})
    except:
        try:
            watched = WatchedProject.objects.get(project_id=project_id, user_id=request.user.pk)
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": False, "watched": True, "can_fork": can_fork,
                                                         'comments': project.get_comments(user.username),
                                                         'can_edit': can_edit})
        except:
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": False, "watched": False, "can_fork": can_fork,
                                                         'comments': project.get_comments(user.username),
                                                         'can_edit': can_edit})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def starred_projects(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'projects.html', {'title': 'Starred projects', 'projects': user.get_starred_projects()})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def my_projects(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'projects.html', {'title': 'My projects', 'projects': user.get_my_projects(),
                                             'can_add': True})


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


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def watched_project_changes(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'updates.html', {'title': 'Watched project changes', 'changes': user.get_watched_changes()})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_watched(request, project_id):
    user = get_object_or_404(GitUser, id=request.user.pk)
    user.add_watched(project_id)
    return redirect('index')


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def remove_watched(request, project_id):
    user = get_object_or_404(GitUser, id=request.user.pk)
    user.remove_watched(project_id)
    return redirect('index')


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def fork_project(request, project_id):
    user = get_object_or_404(GitUser, id=request.user.pk)
    for_fork = get_object_or_404(Project, id=project_id)
    new_project = Project(id=Project.objects.all().order_by('-id')[0].id + 1, lead=user)
    needs_new_title = True
    new_title = '' + for_fork.title
    while needs_new_title:
        try:
            possible_existing = Project.objects.get(lead=user, title=new_title)
            new_title += '_'
        except:
            new_project.title = new_title
            needs_new_title = False
    new_project.save()
    for branch in Branch.objects.filter(project=for_fork):
        new_id = len(Branch.objects.all()) + 1
        branch_copy = Branch(id=new_id, name=branch.name, project=new_project, default=branch.default)
        branch_copy.save()
    return redirect('index')


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def contributors(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.lead.username != request.user.username:
        raise Http404()
    return render(request, 'contributors.html', {'title': 'Contributors', 'contributors': project.get_contributors(),
                                                 'form_action': 'add_contributor/'+str(project_id),
                                                 'other_users': project.get_noncontributors(),
                                                 'project_id': project_id})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_contributor(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.lead.username != request.user.username:
        raise Http404()
    new_contributor = request.POST['new_contributor'].strip()
    new_id = Contributor.objects.all().order_by('-id')[0].id + 1
    con = Contributor(id=new_id, username=new_contributor, project_id=project_id)
    con.save()
    return HttpResponseRedirect(reverse("single_project", args=(project.id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def remove_contributor(request, project_id, username):
    project = get_object_or_404(Project, id=project_id)
    if project.lead.username != request.user.username:
        raise Http404()
    contributor = Contributor.objects.get(username=username, project_id=project_id)
    contributor.delete()
    return HttpResponseRedirect(reverse("single_project", args=(project.id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_project(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    if request.method == 'GET':
        return render(request, 'project_form.html', {'input_value': ''})
    else:
        new_title = request.POST['new_title'].strip()

        error_message = ''
        if new_title is None or new_title == '':
            error_message = 'Project name can\'t be empty'
        elif len(Project.objects.filter(lead=user, title=new_title)) > 0:
            error_message = 'Project with given title already exists'

        if error_message:
            return render(request, 'project_form.html', {'input_value': '', 'error_message': error_message})

        new_id = Project.objects.all().order_by('-id')[0].id + 1
        new_project = Project(id=new_id, title=new_title, lead=user)
        new_project.save()
        return HttpResponseRedirect(reverse("single_project", args=(new_id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect('my_projects')
