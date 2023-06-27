from django.core.management.base import BaseCommand

from ...models import Project


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

    def handle(self, *args, **options):
        self._add_projects()
