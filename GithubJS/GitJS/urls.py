from django.urls import path

from . import views, project_views, branch_views, milestone_views, file_views, \
    comment_and_reaction_views, issue_views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_id>/", project_views.single_project, name="single_project"),
    path("branch/<int:branch_id>", file_views.single_branch, name="single_branch"),
    path("<int:project_id>/add_branch/", branch_views.add_branch, name="add_branch"),
    path("delete_branch/<int:branch_id>", branch_views.delete_branch, name="delete_branch"),
    path("edit_branch/<int:branch_id>", branch_views.edit_branch, name="edit_branch"),
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
    path('my_watched/', project_views.watched_project_changes, name='my_watched'),
    path('fork/<int:project_id>', project_views.fork_project, name='fork'),
    path('my_projects', project_views.my_projects, name='my_projects'),
    path('milestones/<int:project_id>/<str:state>', milestone_views.get_milestones, name='milestones'),
    path('<int:project_id>/add_milestone', milestone_views.add_milestone, name='add_milestone'),
    path('edit_milestone/<int:milestone_id>', milestone_views.edit_milestone, name='edit_milestone'),
    path('delete_milestone/<int:milestone_id>', milestone_views.delete_milestone, name='delete_milestone'),
    path('<int:branch_id>/add_file', file_views.add_file, name='add_file'),
    path('edit_file/<int:file_id>', file_views.edit_file, name='edit_file'),
    path('delete_file/<int:file_id>', file_views.delete_file, name='delete_file'),
    path('contributors/<int:project_id>', project_views.contributors, name='contributors'),
    path('add_contributor/<int:project_id>', project_views.add_contributor, name='add_contributor'),
    path('remove_contributor/<int:project_id>/<str:username>', project_views.remove_contributor,
         name='remove_contributor'),
    path('add_comment/<int:project_id>', comment_and_reaction_views.add_comment, name='add_comment'),
    path('toggle_reaction/<int:comment_id>/<str:reaction_type>', comment_and_reaction_views.toggle_reaction,
         name='toggle_reaction'),
    path('issues/<int:project_id>/<str:state>', issue_views.get_issues, name='issues')
]
