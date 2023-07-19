from django.urls import path

from . import views, project_views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>/", project_views.single_project, name="single_project"),
    path("<int:project_id>/branch/<int:branch_id>", views.single_branch, name="single_branch"),
    path("<int:project_id>/add_branch/", views.add_branch, name="add_branch"),
    path("testredis/", views.cached_initial, name="test_redis_page"),
    path('login/', views.git_login, name='git_login'),
    path('logout/', views.git_logout, name='git_logout'),
    path('register/', views.git_register, name='git_register'),
    path('edit_profile/<int:user_id>', views.edit_profile, name='edit_profile'),
    path('delete_profile/<int:user_id>', views.delete_profile, name='delete_profile'),
    path('add_starred/<int:project_id>', project_views.add_starred, name='add_starred'),
    path('remove_starred/<int:project_id>', project_views.remove_starred, name='remove_starred'),
    path('my_starred/', project_views.starred_projects, name='my_starred'),
    path('start_watch/<int:project_id>', project_views.add_watched, name='add_watched'),
    path('stop_watch/<int:project_id>', project_views.remove_watched, name='remove_watched'),
    path('my_watched/', project_views.watched_project_changes, name='my_watched')
]
