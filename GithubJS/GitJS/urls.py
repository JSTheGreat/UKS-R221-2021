from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.ProjectView.as_view(), name="single_project"),
    path("<int:project_id>/branch/<int:branch_id>", views.single_branch, name="single_branch"),
    path("<int:project_id>/add_branch/", views.add_branch, name="add_branch"),
    path("testredis/", views.cached_initial, name="test_redis_page"),
]
