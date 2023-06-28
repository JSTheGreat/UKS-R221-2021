from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>/", views.single_project, name="single_project"),
    path("<int:project_id>/branch/<int:branch_id>", views.single_branch, name="single_branch"),
]
