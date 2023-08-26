from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Branch


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_branch(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'GET':
        return render(request, "branch_form.html", {"project": project, "title": "New branch", "input_value": "",
                                                    "form_action": str(project_id)+"/add_branch/"})
    else:
        new_branch_name = request.POST['new_branch'].strip()
        if new_branch_name == '':
            error_message = "Branch name can't be empty"
            return render(request, "branch_form.html", {"project": project, "error_message": error_message,
                                                        "title": "Error!", "input_value": "",
                                                        "form_action": str(project_id)+"/add_branch/"})
        new_id = Branch.objects.all().order_by('-id')[0].id + 1
        b = Branch(id=new_id, name=new_branch_name)
        is_default = len(Branch.objects.filter(project=project)) == 0
        b.default = is_default
        b.project = project

        try:
            existing_branch = Branch.objects.get(name=new_branch_name, project_id=project.id)
            error_message = "Branch name already exists"
            return render(request, "branch_form.html", {"project": project, "error_message": error_message,
                                                        "title": "Error!", "input_value": "",
                                                        "form_action": str(project_id)+"/add_branch/"})
        except:
            b.save()
            project.update_users('Branch ' + b.name + ' added to project ' + project.title)
            return HttpResponseRedirect(reverse("single_project", args=(project.id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    project_id = branch.project.id
    is_default = branch.default
    if request.user.username != branch.project.lead.username:
        raise Http404()
    branch.delete()

    if is_default and len(Branch.objects.filter(project=branch.project)) > 0:
        new_default_branch = Branch.objects.filter(project=branch.project)[0]
        new_default_branch.default = True
        new_default_branch.save()

    return HttpResponseRedirect(reverse("single_project", args=(project_id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def edit_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'GET':
        return render(request, "branch_form.html", {"project": branch.project, "title": branch.name,
                                                    "input_value": branch.name,
                                                    "form_action": "edit_branch/" + str(branch_id)})
    else:
        new_branch_name = request.POST['new_branch']
        if new_branch_name.strip() == '':
            error_message = "Branch name can't be empty"
            return render(request, "branch_form.html", {"project": branch.project, "error_message": error_message,
                                                        "title": "Error!", "input_value": branch.name,
                                                        "form_action": "edit_branch/"+str(branch_id)})
        existing_branch = Branch.objects.filter(name=new_branch_name, project_id=branch.project.id)
        if len(existing_branch) > 0:
            if existing_branch[0].id != branch_id:
                error_message = "Branch name already exists"
                return render(request, "branch_form.html", {"project": branch.project, "error_message": error_message,
                                                            "title": "Error!", "input_value": branch.name,
                                                            "form_action": "edit_branch/"+str(branch_id)})
        branch.project.update_users('Branch ' + branch.name + ' changed to ' + new_branch_name)
        branch.name = new_branch_name
        branch.save()
        return HttpResponseRedirect(reverse("single_project", args=(branch.project.id,)))


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def get_commit_history(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    return render(request, "commits.html", {'commits': branch.get_commits(), 'branch': branch})


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def set_default(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    current_default = Branch.objects.get(project=branch.project, default=True)
    current_default.default = False
    current_default.save()

    branch.default = True
    branch.save()
    return HttpResponseRedirect(reverse("single_project", args=(branch.project.id,)))
