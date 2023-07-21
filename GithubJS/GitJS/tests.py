from django.test import TestCase, Client
from django.urls import reverse

from .management.commands.fill_database import Command
from .models import Project, GitUser


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
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/2/')
        self.assertEqual(response.status_code, 200)

    def test_find_project_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/99/')
        self.assertEqual(response.status_code, 404)

    def test_find_non_matching_branch(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/1/branch/2')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('http://localhost:8000/1/branch/5')
        self.assertEqual(response.status_code, 404)

    def test_add_branch_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_branch': '  '}
        response = self.client.post(reverse('add_branch', args=(1,)), context, follow=True)
        self.assertEqual('Branch name can\'t be empty', response.context['error_message'])

    def test_add_branch_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_branch': 'new branch name'}
        response = self.client.post(reverse('add_branch', args=(1,)), context, follow=True)
        self.assertEqual((reverse('single_project', args=(1,)), 302), response.redirect_chain[0])

        project = Project.objects.get(id=1)
        self.assertEqual(project.get_branch_number(), 4)

    def test_login_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertRedirects(response, '/')

    def test_login_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user3'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertTrue(response.context['login_has_error'])

    def test_register_successful(self):
        context = {'uname': 'user4', 'mail': 'sth@mail.com',
                   'psw': 'user4', 'psw_repeat': 'user4', 'role': 'Developer'}
        response = self.client.post('http://localhost:8000/register/', context, follow=True)
        self.assertRedirects(response, '/')

    def test_register_unsuccessful(self):
        context = {'uname': 'user4', 'mail': 'sth@mail.com',
                   'psw': 'user4', 'psw_repeat': 'not_a_repeat', 'role': 'Developer'}
        response = self.client.post('http://localhost:8000/register/', context, follow=True)
        self.assertEqual('Passwords don\'t match!', response.context['error_message'])

    def test_edit_profile(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'uname': 'user1-new', 'mail': 'user1@mailinator.com', 'role': 'Viewer'}
        user_id = GitUser.objects.get(username='user1').id
        response = self.client.post('http://localhost:8000/edit_profile/'+str(user_id), context, follow=True)
        self.assertRedirects(response, '/')

        self.client.logout()

        context = {'uname': 'user1', 'psw': 'user1'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertTrue(response.context['login_has_error'])

        context = {'uname': 'user1-new', 'psw': 'user1'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertRedirects(response, '/')

    def test_delete_profile(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)
        user_id = GitUser.objects.get(username='user1').id
        response = self.client.post('http://localhost:8000/delete_profile/' + str(user_id), follow=True)
        self.assertRedirects(response, '/')

        context = {'uname': 'user1', 'psw': 'user1'}
        response = self.client.post('http://localhost:8000/login/', context, follow=True)
        self.assertTrue(response.context['login_has_error'])

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
