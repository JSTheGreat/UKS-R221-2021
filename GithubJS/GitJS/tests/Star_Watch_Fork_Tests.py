from django.test import TestCase, Client
from django.urls import reverse

from ..management.commands.fill_database import Command
from ..models import Project, GitUser


class StarWatchForkTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # prepare test db for this test suite
        Command().handle()

    def setUp(self) -> None:
        # instantiate client for each test
        self.client = Client()

    def test_get_starred(self):
        user1 = GitUser.objects.get(username='user1')
        starred1 = user1.get_starred_projects()
        self.assertTrue(starred1[0].title == 'Project 2')
        user2 = GitUser.objects.get(username='user2')
        starred2 = user2.get_starred_projects()
        self.assertTrue(starred2[0].title == 'Project 1')

    def test_add_starred(self):
        user2 = GitUser.objects.get(username='user2')
        starred_before = len(user2.get_starred_projects())
        user2.add_starred(3)
        self.assertTrue(len(user2.get_starred_projects()) > starred_before)

    def test_remove_starred(self):
        user2 = GitUser.objects.get(username='user2')
        starred_before = len(user2.get_starred_projects())
        user2.remove_starred(1)
        self.assertTrue(len(user2.get_starred_projects()) < starred_before)
