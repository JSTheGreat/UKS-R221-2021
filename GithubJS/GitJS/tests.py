from django.test import TestCase, Client
from django.urls import reverse

from .management.commands.fill_database import Command
from .models import Project


class InitialTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # prepare test db for this test suite
        Command().handle()

    def setUp(self) -> None:
        # instantiate client for each test
        self.client = Client()

    def test_branch_count(self):
        p1 = Project.objects.get(id=1)
        self.assertIs(p1.get_branch_number(), 3)
        p2 = Project.objects.get(id=2)
        self.assertIs(p2.get_branch_number(), 1)
        p3 = Project.objects.get(id=3)
        self.assertIs(p3.get_branch_number(), 2)

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_find_project_successful(self):
        response = self.client.get('http://localhost:8000/2/')
        self.assertEqual(response.status_code, 200)

    def test_find_project_unsuccessful(self):
        response = self.client.get('http://localhost:8000/99/')
        self.assertEqual(response.status_code, 404)

    def test_find_non_matching_branch(self):
        response = self.client.get('http://localhost:8000/1/branch/2')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('http://localhost:8000/1/branch/5')
        self.assertEqual(response.status_code, 404)

    def test_add_branch_unsuccessful(self):
        context = {'new_branch': '  '}
        response = self.client.post(reverse('add_branch', args=(1,)), context, follow=True)
        self.assertEqual('Branch name can\'t be empty', response.context['error_message'])

    def test_add_branch_successful(self):
        context = {'new_branch': 'new branch name'}
        response = self.client.post(reverse('add_branch', args=(1,)), context, follow=True)
        self.assertEqual((reverse('single_project', args=(1,)), 302), response.redirect_chain[0])

        project = Project.objects.get(id=1)
        self.assertEqual(project.get_branch_number(), 4)

    def test_login_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertEqual(reverse('index'), 302, response.reditert_chain[0])

    def test_login_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user3'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertTrue(response.context['login_has_error'])
