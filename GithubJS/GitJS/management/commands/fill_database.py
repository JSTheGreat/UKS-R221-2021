from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

import datetime

from ...models import Project, Branch, GitUser, StarredProject,\
    WatchedProject, ProjectUpdate, Milestone, File


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

    def _add_milestones(self):
        Milestone.objects.all().delete()

        m1 = Milestone(id=1, title="Milestone 1", description="Desc for milestone no 1", state='OPEN')
        m1.project = Project.objects.get(id=1)
        m1.due_date = timezone.now() + datetime.timedelta(days=20)
        m1.save()

        m2 = Milestone(id=2, title="Milestone 2", description="Desc for milestone no 2", state='CLOSED')
        m2.project = Project.objects.get(id=1)
        m2.due_date = timezone.now() - datetime.timedelta(days=2)
        m2.save()

        m3 = Milestone(id=3, title="Milestone 3", description="Desc for milestone no 3", state='OPEN')
        m3.project = Project.objects.get(id=1)
        m3.due_date = timezone.now() + datetime.timedelta(days=5)
        m3.save()

        m4 = Milestone(id=4, title="Milestone 4", description="Desc for milestone no 4", state='CLOSED')
        m4.project = Project.objects.get(id=2)
        m4.due_date = timezone.now() - datetime.timedelta(days=1)
        m4.save()

        m5 = Milestone(id=5, title="Milestone 5", description="Desc for milestone no 5", state='OPEN')
        m5.project = Project.objects.get(id=2)
        m5.due_date = timezone.now() + datetime.timedelta(days=4)
        m5.save()

    def _add_files(self):
        f1 = File(id=1, title='File 1', text='Generic text for file 1')
        f1.branch = Branch.objects.get(id=1)
        f1.save()

        f2 = File(id=2, title='File 2', text='Generic text for file 2')
        f2.branch = Branch.objects.get(id=1)
        f2.save()

        f3 = File(id=3, title='File 1', text='Generic text for file 1')
        f3.branch = Branch.objects.get(id=2)
        f3.save()

        f4 = File(id=4, title='File 2', text='Generic text for file 2')
        f4.branch = Branch.objects.get(id=3)
        f4.save()

        f5 = File(id=5, title='File 3', text='Generic text for file 3')
        f5.branch = Branch.objects.get(id=4)
        f5.save()

        f6 = File(id=6, title='File 4', text='Generic text for file 4')
        f6.branch = Branch.objects.get(id=5)
        f6.save()

        f7 = File(id=7, title='File 4', text='Generic text for file 4')
        f7.branch = Branch.objects.get(id=6)
        f7.save()

        f8 = File(id=8, title='File 5', text='Generic text for file 5')
        f8.branch = Branch.objects.get(id=6)
        f8.save()

        f9 = File(id=9, title='File 6', text='Generic text for file 6')
        f9.branch = Branch.objects.get(id=1)
        f9.save()

        f10 = File(id=10, title='File 6', text='Generic text for file 6')
        f10.branch = Branch.objects.get(id=3)
        f10.save()

        f11 = File(id=11, title='File 7', text='Generic text for file 7')
        f11.branch = Branch.objects.get(id=5)
        f11.save()

        f12 = File(id=12, title='File 8', text='Generic text for file 8')
        f12.branch = Branch.objects.get(id=6)
        f12.save()

    def handle(self, *args, **options):
        self._add_users()
        self._add_projects()
        self._add_branches()
        self._add_milestones()
        self._add_files()
