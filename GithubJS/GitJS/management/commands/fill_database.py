from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ...models import Project, Branch, GitUser, StarredProject,\
    WatchedProject, ProjectUpdate


class Command(BaseCommand):

    help = 'Komanda za popunjavanje baze sa inicijalnim vrednostima'

    def _add_users(self):
        content_type = ContentType.objects.get_for_model(Project)
        permission1, _ = Permission.objects.get_or_create(
            codename='can_view',
            name='Can view entities',
            content_type=content_type,
        )

        permission2, _ = Permission.objects.get_or_create(
            codename='can_edit',
            name='Can add or edit entities',
            content_type=content_type,
        )

        group1, _ = Group.objects.get_or_create(name="Developer")
        group1.permissions.add(permission1)
        group1.permissions.add(permission2)
        group2, _ = Group.objects.get_or_create(name="Viewer")
        group2.permissions.add(permission1)

        GitUser.objects.all().delete()

        GitUser.objects.create_superuser("admin", "admin@mailinator.com", "admin")

        user1 = GitUser.objects.create_user("user1", "user1@mailinator.com", "user1")
        user1.groups.add(group1)
        user2 = GitUser.objects.create_user("user2", "user2@mailinator.com", "user2")
        user2.groups.add(group2)
        user3 = GitUser.objects.create_user("user3", "user3@mailinator.com", "user3")

        user1.save()
        user2.save()
        user3.save()

    def _add_starred(self, item_id, user_id, project_id):
        sp = StarredProject(id=item_id, user_id=user_id, project_id=project_id)
        sp.save()

    def _add_watched(self, item_id, user_id, project_id):
        wp = WatchedProject(id=item_id, user_id=user_id, project_id=project_id)
        wp.save()

    def _add_projects(self):
        Project.objects.all().delete()
        StarredProject.objects.all().delete()
        WatchedProject.objects.all().delete()
        ProjectUpdate.objects.all().delete()

        p1 = Project(id=1, title="Project 1")
        p1.lead = GitUser.objects.get_by_natural_key("user1")
        p1.save()

        p2 = Project(id=2, title="Project 2")
        p2.lead = GitUser.objects.get_by_natural_key("user2")
        p2.save()

        self._add_starred(1, p2.lead.pk, p1.id)
        self._add_starred(2, p1.lead.pk, p2.id)

        self._add_watched(1, p1.lead.pk, p1.id)
        self._add_watched(2, p2.lead.pk, p1.id)

        p3 = Project(id=3, title="Project 3")
        p3.lead = GitUser.objects.get_by_natural_key("user3")
        p3.save()

    def _get_branch_message(self, branch):
        return 'Branch ' + branch.name + ' added to project ' + branch.project.title

    def _add_branches(self):
        Branch.objects.all().delete()

        b1 = Branch(id=1, name="Branch 1")
        b1.project = Project.objects.get(id=1)
        b1.save()
        b1.project.update_users(self._get_branch_message(b1))

        b2 = Branch(id=2, name="Branch 2")
        b2.project = Project.objects.get(id=1)
        b2.save()
        b2.project.update_users(self._get_branch_message(b2))

        b3 = Branch(id=3, name="Branch 3")
        b3.project = Project.objects.get(id=1)
        b3.save()
        b3.project.update_users(self._get_branch_message(b3))

        b4 = Branch(id=4, name="Branch 4")
        b4.project = Project.objects.get(id=2)
        b4.save()
        b4.project.update_users(self._get_branch_message(b4))

        b5 = Branch(id=5, name="Branch 5")
        b5.project = Project.objects.get(id=3)
        b5.save()
        b5.project.update_users(self._get_branch_message(b5))

        b6 = Branch(id=6, name="Branch 6")
        b6.project = Project.objects.get(id=3)
        b6.save()
        b6.project.update_users(self._get_branch_message(b6))

    def handle(self, *args, **options):
        self._add_users()
        self._add_projects()
        self._add_branches()
