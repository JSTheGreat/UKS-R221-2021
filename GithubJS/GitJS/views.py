from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from .models import Project, Branch, GitUser

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
import redis

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def index(request):
    return render(request, "index.html", {"title": "Index"})


@cache_page(CACHE_TTL)
def cached_initial(request):
    redis.Redis(host='uks_js_redis', port=6379)
    return render(request, "cache_test.html", {"title": "Redis test"})


def git_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'GET':
        return render(request, "login.html", {"title": "Log In"})
    elif request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['psw']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, "login.html", {"title": "Login error!", 'login_has_error': True})
    else:
        raise Http404()


def edit_profile(request, user_id):
    user = get_object_or_404(GitUser, id=user_id)
    role = ''
    if len(user.groups.all()) > 0:
        if user.groups.all()[0].name == 'Developer':
            role = 'Developer'
        else:
            role = 'Viewer'
    if request.method == 'GET':
        return render(request, "register.html", {"title": "Edit profile", "user": {
            "uname": user.username, "mail": user.email, "role": role
        }, "form_action": 'edit_profile/' + str(user_id)})
    elif request.method == 'POST':

        username = request.POST['uname']
        email = request.POST['mail']
        role = request.POST['role']

        error_message = ''

        if username.strip() == '' or username is None:
            error_message = 'Username can\'t remain empty!'
        if email.strip() == '' or email is None:
            error_message = 'Email can\'t remain empty!'
        elif role.strip() == '' or role is None:
            error_message = 'You have to pick a role!'

        if error_message:
            return render(request, "register.html", {"title": "Update profile error!", 'error_message': error_message,
                                                     "user": {
                                                        "uname": user.username, "mail": user.email, "role": role
                                                        },
                                                     "form_action": 'edit_profile/' + str(user_id)})

        user.username = username
        user.email = email
        user.groups.all().delete()
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        user.save()
        return redirect('index')


def delete_profile(request, user_id):
    user = get_object_or_404(GitUser, id=user_id)
    user.delete()
    return redirect('index')


def git_register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'GET':
        return render(request, "register.html", {"title": "Register", "user": {
            "uname": "", "mail": "", "role": "Developer"
        }, "form_action": "register/"})
    elif request.method == 'POST':
        username = request.POST['uname']
        email = request.POST['mail']
        password = request.POST['psw']
        repeated = request.POST['psw_repeat']
        role = request.POST['role']

        error_message = ''

        if username.strip() == '' or username is None:
            error_message = 'Username can\'t remain empty!'
        elif email.strip() == '' or email is None:
            error_message = 'Email can\'t remain empty!'
        elif password.strip() == '' or password is None:
            error_message = 'Password can\'t remain empty!'
        elif repeated.strip() == '' or repeated is None:
            error_message = 'Password must be repeated!'
        elif password.strip() != repeated:
            error_message = 'Passwords don\'t match!'
        elif role.strip() == '' or role is None:
            error_message = 'You have to pick a role!'

        if error_message:
            return render(request, "register.html", {"title": "Register error!", 'error_message': error_message,
                                                     "user": {"uname": "", "mail": "",
                                                              "role": "Developer"},
                                                     "form_action": "register/"})

        group, _ = Group.objects.get_or_create(name=role)
        new_user = GitUser.objects.create_user(username, email, password)
        new_user.groups.add(group)
        new_user.save()

        login(request, new_user)
        return redirect('index')
    else:
        raise Http404()


def git_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index')
    raise PermissionDenied()
