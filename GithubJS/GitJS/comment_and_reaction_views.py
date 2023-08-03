from django.utils import timezone
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Comment, GitUser


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "project_view.html", {"project": project, "title": project.title,
                                                     'comments': project.get_comments()})
    else:
        new_comment = request.POST['new_comment'].strip()
        error_message = ''
        if new_comment == '':
            error_message = "You can't submit an empty comment"
        if error_message:
            return render(request, "project_view.html", {"project": project, "title": project.title,
                                                         "error_message": error_message,
                                                         'comments': project.get_comments()})

        new_id = len(Comment.objects.all())+1
        comment = Comment(id=new_id, text=new_comment, last_update=timezone.now())
        comment.project = project
        comment.user = GitUser.objects.get_by_natural_key(request.user.username)
        comment.save()
        return render(request, "project_view.html", {"project": project, "title": project.title,
                                                     'comments': comment.project.get_comments()})
