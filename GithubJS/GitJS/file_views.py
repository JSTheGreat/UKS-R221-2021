from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Branch, File


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def single_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return render(request, 'branch_view.html', {"branch": branch, "title": "Single branch"})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_file(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'GET':
        return render(request, "file_edit.html", {"branch": branch, "title": "New file", "file_title": "",
                                                  "file_text": "", "form_action": str(branch_id)+"/add_file"})
    else:
        file_title = request.POST['new_title'].strip()
        file_text = request.POST['new_text'].strip()
        if file_title == '':
            error_message = "File title can't be empty"
            return render(request, "file_edit.html", {"branch": branch, "title": "New file", "file_title": "",
                                                      "error_message": error_message,
                                                      "file_text": "", "form_action": str(branch_id)+"/add_file"})
        new_id = len(File.objects.all())+1
        f = File(id=new_id, title=file_title, text=file_text)
        f.branch = branch
        try:
            existing_file = File.objects.get(title=file_title, branch=branch)
            error_message = "File with given title already exists"
            return render(request, "file_edit.html", {"branch": branch, "error_message": error_message,
                                                      "title": "Error!", "file_title": "", "file_text": "",
                                                      "form_action": str(branch_id)+"/add_file"})
        except:
            f.save()
            branch.project.update_users('File ' + f.title + ' added to ' + branch.project.title + ' on ' + branch.name)
            return HttpResponseRedirect(reverse("single_branch", args=(branch_id,)))
