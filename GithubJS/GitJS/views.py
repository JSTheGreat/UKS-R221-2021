from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def single_project(request, project_id):
    return HttpResponse("You are looking at project ID=" + str(project_id))
