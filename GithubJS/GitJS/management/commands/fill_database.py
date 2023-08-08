from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

import datetime

from ...models import Project, Branch, GitUser, StarredProject,\
    WatchedProject, ProjectUpdate, Milestone, File, Contributor, \
    Comment, Reaction, Issue


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

        user4 = GitUser.objects.create_user("user4", "user4@mailinator.com", "user4")
        user4.groups.add(group1)
        user5 = GitUser.objects.create_user("user5", "user5@mailinator.com", "user5")
        user5.groups.add(group2)
        user6 = GitUser.objects.create_user("user6", "user6@mailinator.com", "user6")
        user6.groups.add(group1)

        user1.save()
        user2.save()
        user3.save()

    def _add_starred(self, item_id, user_id, project_id):
        sp = StarredProject(id=item_id, user_id=user_id, project_id=project_id)
        sp.save()

    def _add_watched(self, item_id, user_id, project_id):
        wp = WatchedProject(id=item_id, user_id=user_id, project_id=project_id)
        wp.save()

    def _add_contributor(self, item_id, username, project_id):
        c = Contributor(id=item_id, username=username, project_id=project_id)
        c.save()

    def _add_projects(self):
        Project.objects.all().delete()
        StarredProject.objects.all().delete()
        WatchedProject.objects.all().delete()
        ProjectUpdate.objects.all().delete()
        Contributor.objects.all().delete()

        p1 = Project(id=1, title="Project 1")
        p1.lead = GitUser.objects.get_by_natural_key("user1")
        p1.save()

        p2 = Project(id=2, title="Project 2")
        p2.lead = GitUser.objects.get_by_natural_key("user5")
        p2.save()

        p3 = Project(id=3, title="Project 3")
        p3.lead = GitUser.objects.get_by_natural_key("user6")
        p3.save()

        self._add_starred(1, p2.lead.pk, p1.id)
        self._add_starred(2, p1.lead.pk, p2.id)

        self._add_watched(1, p1.lead.pk, p1.id)
        self._add_watched(2, p2.lead.pk, p1.id)

        self._add_contributor(1, GitUser.objects.get_by_natural_key("user4").username, p1.id)
        self._add_contributor(2, GitUser.objects.get_by_natural_key("user5").username, p1.id)
        self._add_contributor(3, GitUser.objects.get_by_natural_key("user6").username, p2.id)

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

    def _add_comments(self):
        c1 = Comment(id=1, text='Text for comment no 1')
        c1.last_update = timezone.now() - datetime.timedelta(days=1)
        c1.user = GitUser.objects.get_by_natural_key("user4")
        c1.project = Project.objects.get(id=1)
        c1.save()

        c2 = Comment(id=2, text='Text for comment no 2')
        c2.last_update = timezone.now() - datetime.timedelta(days=2)
        c2.user = GitUser.objects.get_by_natural_key("user6")
        c2.project = Project.objects.get(id=1)
        c2.save()

        c3 = Comment(id=3, text='Text for comment no 3')
        c3.last_update = timezone.now() - datetime.timedelta(days=3)
        c3.user = GitUser.objects.get_by_natural_key("user1")
        c3.project = Project.objects.get(id=1)
        c3.save()

        c4 = Comment(id=4, text='Text for comment no 4')
        c4.last_update = timezone.now() - datetime.timedelta(days=3)
        c4.user = GitUser.objects.get_by_natural_key("user4")
        c4.project = Project.objects.get(id=2)
        c4.save()

        c5 = Comment(id=5, text='Text for comment no 5')
        c5.last_update = timezone.now() - datetime.timedelta(days=1)
        c5.user = GitUser.objects.get_by_natural_key("user6")
        c5.project = Project.objects.get(id=2)
        c5.save()

        c6 = Comment(id=6, text='Text for comment no 6')
        c6.last_update = timezone.now() - datetime.timedelta(days=4)
        c6.user = GitUser.objects.get_by_natural_key("user2")
        c6.project = Project.objects.get(id=3)
        c6.save()

    def _add_reactions(self):
        r1 = Reaction(id=1, type='LIKE')
        r1.user = GitUser.objects.get_by_natural_key("user2")
        r1.comment = Comment.objects.get(id=1)
        r1.save()

        r2 = Reaction(id=2, type='DISLIKE')
        r2.user = GitUser.objects.get_by_natural_key("user4")
        r2.comment = Comment.objects.get(id=1)
        r2.save()

        r3 = Reaction(id=3, type='LIKE')
        r3.user = GitUser.objects.get_by_natural_key("user1")
        r3.comment = Comment.objects.get(id=2)
        r3.save()

        r4 = Reaction(id=4, type='DISLIKE')
        r4.user = GitUser.objects.get_by_natural_key("user5")
        r4.comment = Comment.objects.get(id=2)
        r4.save()

        r5 = Reaction(id=5, type='DISLIKE')
        r5.user = GitUser.objects.get_by_natural_key("user6")
        r5.comment = Comment.objects.get(id=3)
        r5.save()

        r6 = Reaction(id=6, type='DISLIKE')
        r6.user = GitUser.objects.get_by_natural_key("user1")
        r6.comment = Comment.objects.get(id=3)
        r6.save()

        r7 = Reaction(id=7, type='LIKE')
        r7.user = GitUser.objects.get_by_natural_key("user5")
        r7.comment = Comment.objects.get(id=4)
        r7.save()

        r8 = Reaction(id=8, type='LIKE')
        r8.user = GitUser.objects.get_by_natural_key("user2")
        r8.comment = Comment.objects.get(id=4)
        r8.save()

        r9 = Reaction(id=9, type='LIKE')
        r9.user = GitUser.objects.get_by_natural_key("user4")
        r9.comment = Comment.objects.get(id=5)
        r9.save()

        r10 = Reaction(id=10, type='DISLIKE')
        r10.user = GitUser.objects.get_by_natural_key("user4")
        r10.comment = Comment.objects.get(id=6)
        r10.save()

    def _add_issues(self):
        i1 = Issue(id=1, title='Issue 1', description='Description text for issue no 1', state='OPEN')
        i1.project = Project.objects.get(id=1)
        i1.milestone = Milestone.objects.get(id=1)
        i1.save()

        i2 = Issue(id=2, title='Issue 2', description='Description text for issue no 2', state='CLOSED')
        i2.project = Project.objects.get(id=1)
        i2.milestone = Milestone.objects.get(id=2)
        i2.save()

        i3 = Issue(id=3, title='Issue 3', description='Description text for issue no 3', state='OPEN')
        i3.project = Project.objects.get(id=1)
        i3.milestone = Milestone.objects.get(id=1)
        i3.save()

        i4 = Issue(id=4, title='Issue 4', description='Description text for issue no 4', state='OPEN')
        i4.project = Project.objects.get(id=1)
        i4.milestone = Milestone.objects.get(id=3)
        i4.save()

        i5 = Issue(id=5, title='Issue 5', description='Description text for issue no 5', state='CLOSED')
        i5.project = Project.objects.get(id=2)
        i5.milestone = Milestone.objects.get(id=4)
        i5.save()

        i6 = Issue(id=6, title='Issue 6', description='Description text for issue no 6', state='OPEN')
        i6.project = Project.objects.get(id=2)
        i6.milestone = Milestone.objects.get(id=5)
        i6.save()

        i7 = Issue(id=7, title='Issue 7', description='Description text for issue no 7', state='OPEN')
        i7.project = Project.objects.get(id=3)
        i7.save()

    def handle(self, *args, **options):
        self._add_users()
        self._add_projects()
        self._add_branches()
        self._add_milestones()
        self._add_files()
        self._add_comments()
        self._add_reactions()
        self._add_issues()
