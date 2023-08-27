import datetime

from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse

from .models import Project, Milestone


@login_required(login_url='login/')
@permission_required('GitJS.can_view', raise_exception=True)
def get_milestones(request, project_id, state):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    return render(request, 'milestones.html', {'title': 'Milestones for ' + project.title, 'project_id': project_id,
                                               'milestones': project.get_milestones(state),
                                               'can_edit': can_edit})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def add_milestone(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    can_edit = project.can_edit(request.user.username)
    if request.method == 'GET':
        return render(request, 'milestone_form.html', {'title': 'New milestone', 'project_id': project_id,
                                                       'form_action': str(project_id)+'/add_milestone',
                                                       'can_edit': can_edit,
                                                       'input_title': '', 'input_desc': '', 'due_date': timezone.now()
                                                       })
    else:
        new_title = request.POST['new_title'].strip()
        new_desc = request.POST['new_desc'].strip()
        due_date = datetime.datetime.strptime(request.POST['due_date'], "%Y-%m-%d")

        error_message = ''
        if new_title == '' or new_title is None:
            error_message = 'Title can\'t be empty'
        elif new_desc == '' or new_desc is None:
            error_message = 'Description can\'t be empty'
        elif due_date.date() <= timezone.now().date():
            error_message = 'Due date has to be a future date'

        if error_message:
            return render(request, 'milestone_form.html', {'title': 'New milestone', 'project_id': project_id,
                                                           'form_action': str(project_id) + '/add_milestone',
                                                           'input_title': '', 'input_desc': '',
                                                           'due_date': timezone.now(),
                                                           'error_message': error_message,
                                                           'can_edit': can_edit
                                                           })

        try:
            existing = Milestone.objects.get(title=new_title, project=project)
            error_message = "Milestone with given title already exists"
            return render(request, 'milestone_form.html', {'title': 'New milestone', 'project_id': project_id,
                                                           'form_action': str(project_id) + '/add_milestone',
                                                           'input_title': '', 'input_desc': '',
                                                           'due_date': timezone.now(),
                                                           'error_message': error_message,
                                                           'can_edit': can_edit
                                                           })
        except:
            new_id = len(Milestone.objects.all())
            milestone = Milestone(id=new_id, title=new_title, description=new_desc, due_date=due_date, state='OPEN')
            milestone.project = project
            milestone.project.update_users('Milestone ' + milestone.title + ' added')
            milestone.save()
            return render(request, 'milestones.html',
                          {'title': 'Milestones for ' + project.title, 'project_id': project_id,
                           'milestones': project.get_milestones('OPEN')})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def edit_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    date_val = milestone.due_date.isoformat().split("T")[0]
    can_edit = milestone.project.can_edit(request.user.username)
    if request.method == 'GET':
        return render(request, 'milestone_form.html', {'title': 'Milestone #'+str(milestone_id),
                                                       'project_id': milestone.project.id,
                                                       'percent': milestone.get_percent(),
                                                       'form_action': 'edit_milestone/'+str(milestone_id),
                                                       'input_title': milestone.title,
                                                       'input_desc': milestone.description,
                                                       'due_date': date_val,
                                                       'can_edit': can_edit
                                                       })
    else:
        new_title = request.POST['new_title'].strip()
        new_desc = request.POST['new_desc'].strip()
        due_date = datetime.datetime.strptime(request.POST['due_date'], "%Y-%m-%d")

        error_message = ''
        if new_title == '' or new_title is None:
            error_message = 'Title can\'t be empty'
        elif new_desc == '' or new_desc is None:
            error_message = 'Description can\'t be empty'
        elif due_date.date() <= timezone.now().date():
            error_message = 'Due date has to be a future date'

        if error_message:
            return render(request, 'milestone_form.html', {'title': 'Milestone #'+str(milestone_id),
                                                           'project_id': milestone.project.id,
                                                           'percent': milestone.get_percent(),
                                                           'form_action': 'edit_milestone/' + str(milestone_id),
                                                           'input_title': milestone.title,
                                                           'input_desc': milestone.description,
                                                           'due_date': date_val,
                                                           'error_message': error_message,
                                                           'can_edit': can_edit
                                                           })

        existing = Milestone.objects.filter(title=new_title, project=milestone.project)
        if len(existing) > 0:
            if existing[0].id != milestone.id:
                error_message = "Milestone with given title already exists"
                return render(request, 'milestone_form.html', {'title': 'Milestone #'+str(milestone_id),
                                                               'project_id': milestone.project.id,
                                                               'percent': milestone.get_percent(),
                                                               'form_action': 'edit_milestone/' + str(milestone_id),
                                                               'input_title': milestone.title,
                                                               'input_desc': milestone.description,
                                                               'due_date': date_val,
                                                               'error_message': error_message,
                                                               'can_edit': can_edit
                                                               })

        milestone.project.update_users('Milestone ' + milestone.title + ' changed')
        milestone.title = new_title
        milestone.description = new_desc
        milestone.due_date = due_date
        milestone.save()
        return render(request, 'milestones.html',
                      {'title': 'Milestones for ' + milestone.project.title, 'project_id': milestone.project.id,
                       'milestones': milestone.project.get_milestones('OPEN')})


@login_required(login_url='login/')
@permission_required('GitJS.can_edit', raise_exception=True)
def toggle_milestone_status(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    if milestone.state == 'OPEN':
        milestone.state = 'CLOSED'
        milestone.project.update_users('Milestone ' + milestone.title + ' closed in ' + milestone.project.title)
    else:
        milestone.state = 'OPEN'
        milestone.project.update_users('Milestone ' + milestone.title + ' opened in ' + milestone.project.title)
    milestone.save()
    return HttpResponseRedirect(reverse("milestones", args=(milestone.project.id, 'OPEN',)))
