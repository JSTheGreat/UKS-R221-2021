from django.utils import timezone

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Branch, File, Commit


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def single_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    can_edit = branch.project.can_edit(request.user.username)
    return render(request, 'branch_view.html', {"branch": branch, "title": "Single branch",
                                                'can_edit': can_edit})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_file(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    can_edit = branch.project.can_edit(request.user.username)
    if request.user.username not in branch.project.get_all_participants():
        return HttpResponseRedirect(reverse("single_branch", args=(branch_id,)))
    if request.method == 'GET':
        return render(request, "file_edit.html", {"branch": branch, "title": "New file", "file_title": "",
                                                  "file_text": "", "form_action": str(branch_id)+"/add_file",
                                                  'can_edit': can_edit})
    else:
        file_title = request.POST['new_title'].strip()
        file_text = request.POST['new_text'].strip()
        if file_title == '':
            error_message = "File title can't be empty"
            return render(request, "file_edit.html", {"branch": branch, "title": "New file", "file_title": "",
                                                      "error_message": error_message,
                                                      "file_text": "", "form_action": str(branch_id)+"/add_file",
                                                      'can_edit': can_edit})
        new_id = len(File.objects.all())+1
        f = File(id=new_id, title=file_title, text=file_text)
        f.branch = branch
        try:
            existing_file = File.objects.get(title=file_title, branch=branch)
            error_message = "File with given title already exists"
            return render(request, "file_edit.html", {"branch": branch, "error_message": error_message,
                                                      "title": "Error!", "file_title": "", "file_text": "",
                                                      "form_action": str(branch_id)+"/add_file",
                                                      'can_edit': can_edit})
        except:
            f.save()
            new_commit_id = Commit.objects.all().order_by('-id')[0].id + 1
            commit = Commit(id=new_commit_id, branch=branch, committer=request.user.username, date_time=timezone.now())
            commit.log_message = 'File '+f.title+' added'
            commit.save()
            return HttpResponseRedirect(reverse("single_branch", args=(branch_id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def edit_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    can_edit = file.branch.project.can_edit(request.user.username)
    if request.method == 'GET':
        return render(request, "file_edit.html", {"branch": file.branch, "title": "Edit file", "file_title": file.title,
                                                  "file_text": file.text, "form_action": "edit_file/" + str(file_id),
                                                  'can_edit': can_edit})
    else:
        file_title = request.POST['new_title'].strip()
        file_text = request.POST['new_text'].strip()
        if file_title == '':
            error_message = "File title can't be empty"
            return render(request, "file_edit.html", {"branch": file.branch, "title": "Error!",
                                                      "file_title": file.title, "file_text": file.text,
                                                      "error_message": error_message,
                                                      "form_action": "edit_file/" + str(file_id),
                                                      'can_edit': can_edit})
        existing_files = File.objects.filter(title=file_title, branch=file.branch)
        if len(existing_files) > 0:
            if existing_files[0].id != file_id:
                error_message = "File with given title already exists"
                return render(request, "file_edit.html", {"branch": file.branch, "title": "Error!",
                                                          "file_title": file.title, "file_text": file.text,
                                                          "error_message": error_message,
                                                          "form_action": "edit_file/" + str(file_id),
                                                          'can_edit': can_edit})
        new_commit_id = Commit.objects.all().order_by('-id')[0].id + 1
        commit = Commit(id=new_commit_id, branch=file.branch, committer=request.user.username,
                        date_time=timezone.now())
        commit.log_message = 'File ' + file.title + ' changed'
        file.title = file_title
        file.text = file_text
        file.save()
        commit.save()
        return HttpResponseRedirect(reverse("single_branch", args=(file.branch.id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if request.user.username not in file.branch.project.get_all_participants():
        return HttpResponseRedirect(reverse("single_branch", args=(file.branch.id,)))
    new_commit_id = Commit.objects.all().order_by('-id')[0].id + 1
    commit = Commit(id=new_commit_id, branch=file.branch, committer=request.user.username,
                    date_time=timezone.now())
    commit.log_message = 'File ' + file.title + ' deleted'
    file.delete()
    commit.save()
    return HttpResponseRedirect(reverse("single_branch", args=(file.branch.id,)))
