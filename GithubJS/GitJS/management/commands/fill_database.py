from django.core.management.base import BaseCommand

from ...models import Project, Branch


class Command(BaseCommand):

    help = 'Komanda za popunjavanje baze sa inicijalnim vrednostima'

    def _add_projects(self):
        Project.objects.all().delete()

        p1 = Project(id=1, title="Project 1")
        p1.save()

        p2 = Project(id=2, title="Project 2")
        p2.save()

        p3 = Project(id=3, title="Project 3")
        p3.save()

    def _add_branches(self):
        Branch.objects.all().delete()

        b1 = Branch(id=1, name="Branch 1")
        b1.project = Project.objects.get(id=1)
        b1.save()

        b2 = Branch(id=2, name="Branch 2")
        b2.project = Project.objects.get(id=1)
        b2.save()

        b3 = Branch(id=3, name="Branch 3")
        b3.project = Project.objects.get(id=1)
        b3.save()

        b4 = Branch(id=4, name="Branch 4")
        b4.project = Project.objects.get(id=2)
        b4.save()

        b5 = Branch(id=5, name="Branch 5")
        b5.project = Project.objects.get(id=3)
        b5.save()

        b6 = Branch(id=6, name="Branch 6")
        b6.project = Project.objects.get(id=3)
        b6.save()

    def handle(self, *args, **options):
        self._add_projects()
        self._add_branches()
