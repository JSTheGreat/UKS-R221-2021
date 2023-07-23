from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from .models import Project, Branch, GitUser, StarredProject, WatchedProject


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def single_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(GitUser, id=request.user.pk)
    can_fork = project.lead.id != user.id
    try:
        starred = StarredProject.objects.get(project_id=project_id, user_id=request.user.pk)
        try:
            watched = WatchedProject.objects.get(project_id=project_id, user_id=request.user.pk)
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": True, "watched": True, "can_fork": can_fork})
        except:
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": True, "watched": False, "can_fork": can_fork})
    except:
        try:
            watched = WatchedProject.objects.get(project_id=project_id, user_id=request.user.pk)
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": False, "watched": True, "can_fork": can_fork})
        except:
            return render(request, 'project_view.html', {'title': project.title, "project": project,
                                                         "starred": False, "watched": False, "can_fork": can_fork})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def starred_projects(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'projects.html', {'title': 'Starred projects', 'projects': user.get_starred_projects()})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def my_projects(request):
    user = get_object_or_404(GitUser, id=request.user.pk)
    return render(request, 'projects.html', {'title': 'My projects', 'projects': user.get_my_projects()})


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
    new_project = Project(id=len(Project.objects.all()) + 1, lead=user)
    needs_new_title = True
    new_title = '' + for_fork.title
    while needs_new_title:
        try:
            possible_existing = Project.objects.get(lead=user, title=new_title)
            print("Existing project found!")
            new_title += '_'
            print("New title for existing project: " + new_title)
        except:
            print("No project found!")
            new_project.title = new_title
            print("new title for forked project: " + new_title)
            needs_new_title = False
    new_project.save()
    for branch in Branch.objects.filter(project=for_fork):
        new_id = len(Branch.objects.all()) + 1
        branch_copy = Branch(id=new_id, name=branch.name, project=new_project)
        branch_copy.save()
    return redirect('index')
