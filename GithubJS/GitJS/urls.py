from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>/", views.project_view, name="single_project"),
    path("<int:project_id>/branch/<int:branch_id>", views.single_branch, name="single_branch"),
    path("<int:project_id>/add_branch/", views.add_branch, name="add_branch"),
    path("testredis/", views.cached_initial, name="test_redis_page"),
    path('login/', views.git_login, name='git_login'),
    path('logout/', views.git_logout, name='git_logout'),
    path('register/', views.git_register, name='git_register'),
    path('edit_profile/<int:user_id>', views.edit_profile, name='edit_profile'),
    path('delete_profile/<int:user_id>', views.delete_profile, name='delete_profile')
]
