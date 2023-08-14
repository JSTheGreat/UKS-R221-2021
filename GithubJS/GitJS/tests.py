from django.test import TestCase, Client
from django.urls import reverse

from .management.commands.fill_database import Command
from .models import Project, GitUser, Branch, Milestone, File, Comment, Reaction, Issue


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
        context = {'uname': 'user7', 'mail': 'sth@mail.com',
                   'psw': 'user7', 'psw_repeat': 'user7', 'role': 'Developer'}
        response = self.client.post('http://localhost:8000/register/', context, follow=True)
        self.assertRedirects(response, '/')

    def test_register_unsuccessful(self):
        context = {'uname': 'user7', 'mail': 'sth@mail.com',
                   'psw': 'user7', 'psw_repeat': 'not_a_repeat', 'role': 'Developer'}
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
        user5 = GitUser.objects.get(username='user5')
        starred2 = user5.get_starred_projects()
        self.assertTrue(starred2[0].title == 'Project 1')

    def test_add_starred(self):
        user5 = GitUser.objects.get(username='user5')
        starred_before = len(user5.get_starred_projects())
        user5.add_starred(3)
        self.assertTrue(len(user5.get_starred_projects()) > starred_before)

    def test_remove_starred(self):
        user5 = GitUser.objects.get(username='user5')
        starred_before = len(user5.get_starred_projects())
        user5.remove_starred(1)
        self.assertTrue(len(user5.get_starred_projects()) < starred_before)

    def test_get_watched(self):
        user1 = GitUser.objects.get(username='user1')
        watched1 = user1.get_watched_changes()
        self.assertTrue(watched1[0].message == 'Branch Branch 3 added to project Project 1')
        self.assertTrue(watched1[1].message == 'Branch Branch 2 added to project Project 1')
        self.assertTrue(watched1[2].message == 'Branch Branch 1 added to project Project 1')
        user5 = GitUser.objects.get(username='user5')
        watched2 = user5.get_watched_changes()
        self.assertTrue(watched2[0].message == 'Branch Branch 3 added to project Project 1')
        self.assertTrue(watched2[1].message == 'Branch Branch 2 added to project Project 1')
        self.assertTrue(watched2[2].message == 'Branch Branch 1 added to project Project 1')

    def test_add_watched(self):
        user5 = GitUser.objects.get(username='user5')
        watched_before = len(user5.get_watched_changes())
        user5.add_watched(3)
        watched_project = Project.objects.get(id=3)
        watched_project.update_users("Generic update message")
        self.assertTrue(len(user5.get_watched_changes()) > watched_before)

    def test_remove_watched(self):
        user5 = GitUser.objects.get(username='user5')
        watched_before = len(user5.get_watched_changes())
        user5.remove_watched(1)
        unwatched_project = Project.objects.get(id=3)
        unwatched_project.update_users("Generic update message")
        self.assertTrue(len(user5.get_watched_changes()) == watched_before)

    def test_get_starred_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/my_starred', follow=True)
        starred_project = Project.objects.get(id=2)
        self.assertTrue(starred_project in response.context['projects'])

    def test_get_watched_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/my_watched', follow=True)
        watched_changes = response.context['changes']
        self.assertEqual(watched_changes[0].message, 'Branch Branch 3 added to project Project 1')
        self.assertEqual(watched_changes[1].message, 'Branch Branch 2 added to project Project 1')
        self.assertEqual(watched_changes[2].message, 'Branch Branch 1 added to project Project 1')

    def test_add_starred_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/add_starred/3', follow=True)
        self.assertRedirects(response, '/')
        starred_project = Project.objects.get(id=3)
        response = self.client.get('http://localhost:8000/my_starred', follow=True)
        self.assertTrue(starred_project in response.context['projects'])

    def test_remove_starred_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/remove_starred/2', follow=True)
        self.assertRedirects(response, '/')
        starred_project = Project.objects.get(id=2)
        response = self.client.get('http://localhost:8000/my_starred', follow=True)
        self.assertTrue(starred_project not in response.context['projects'])

    def test_add_watched_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/start_watch/3', follow=True)
        self.assertRedirects(response, '/')
        watched_project = Project.objects.get(id=3)
        watched_project.update_users('Generic update message')
        response = self.client.get('http://localhost:8000/my_watched', follow=True)
        self.assertEqual(response.context['changes'][0].message, 'Generic update message')

    def test_remove_watched_client(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/stop_watch/1', follow=True)
        self.assertRedirects(response, '/')
        watched_project = Project.objects.get(id=3)
        watched_project.update_users('Generic update message')
        response = self.client.get('http://localhost:8000/my_watched', follow=True)
        self.assertNotEqual(response.context['changes'][0].message, 'Generic update message')

    def test_fork(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.get('http://localhost:8000/my_projects', follow=True)
        size_before = len(response.context['projects'])
        response = self.client.get('http://localhost:8000/fork/2', follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get('http://localhost:8000/my_projects', follow=True)
        self.assertTrue(len(response.context['projects']) > size_before)

    def test_edit_branch_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        branch_before = Branch.objects.get(id=1).name
        context = {'new_branch': 'new branch name'}
        response = self.client.post(reverse('edit_branch', args=(1,)), context, follow=True)
        self.assertNotEqual(branch_before, Branch.objects.get(id=1).name)

    def test_edit_branch_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_branch': '  '}
        response = self.client.post(reverse('edit_branch', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Branch name can\'t be empty')

        context = {'new_branch': 'Branch 2'}
        response = self.client.post(reverse('edit_branch', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Branch name already exists')

    def test_delete_branch_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        branch_size_before = len(Branch.objects.all())
        self.client.post(reverse('delete_branch', args=(1,)), context, follow=True)
        self.assertTrue(branch_size_before > len(Branch.objects.all()))

    def test_delete_branch_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user2'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.post(reverse('delete_branch', args=(1,)), context, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_milestones(self):
        p1 = Project.objects.get(id=1)
        open1 = p1.get_milestones('OPEN')
        self.assertEqual(len(open1), 2)
        closed1 = p1.get_milestones('CLOSED')
        self.assertEqual(len(closed1), 1)

        p2 = Project.objects.get(id=2)
        open2 = p2.get_milestones('OPEN')
        self.assertEqual(len(open2), 1)
        closed2 = p2.get_milestones('CLOSED')
        self.assertEqual(len(closed2), 1)

    def test_add_milestone_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'New title', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        project = Project.objects.get(id=1)
        size_before = len(project.get_milestones('OPEN'))
        response = self.client.post(reverse('add_milestone', args=(1,)), context, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(project.get_milestones('OPEN')) > size_before)

    def test_add_milestone_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '  ', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('add_milestone', args=(1,)), context, follow=True)
        self.assertEqual('Title can\'t be empty', response.context['error_message'])

        context = {'new_title': 'New title', 'new_desc': '   ', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('add_milestone', args=(1,)), context, follow=True)
        self.assertEqual('Description can\'t be empty', response.context['error_message'])

        context = {'new_title': 'New title', 'new_desc': 'New Description', 'due_date': '2023-06-06'}
        response = self.client.post(reverse('add_milestone', args=(1,)), context, follow=True)
        self.assertEqual('Due date has to be a future date', response.context['error_message'])

        context = {'new_title': 'Milestone 1', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('add_milestone', args=(1,)), context, follow=True)
        self.assertEqual('Milestone with given title already exists', response.context['error_message'])

    def test_edit_milestone_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        milestone_before = Milestone.objects.get(id=3)
        context = {'new_title': 'New title', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        self.client.post(reverse('edit_milestone', args=(3,)), context, follow=True)
        milestone_after = Milestone.objects.get(id=3)
        self.assertNotEqual(milestone_before.title, milestone_after.title)
        self.assertNotEqual(milestone_before.description, milestone_after.description)
        self.assertNotEqual(milestone_before.due_date, milestone_after.due_date)

    def test_edit_milestone_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '  ', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('edit_milestone', args=(3,)), context, follow=True)
        self.assertEqual('Title can\'t be empty', response.context['error_message'])

        context = {'new_title': 'New title', 'new_desc': '   ', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('edit_milestone', args=(3,)), context, follow=True)
        self.assertEqual('Description can\'t be empty', response.context['error_message'])

        context = {'new_title': 'New title', 'new_desc': 'New Description', 'due_date': '2023-06-06'}
        response = self.client.post(reverse('edit_milestone', args=(3,)), context, follow=True)
        self.assertEqual('Due date has to be a future date', response.context['error_message'])

        context = {'new_title': 'Milestone 1', 'new_desc': 'New Description', 'due_date': '2024-10-10'}
        response = self.client.post(reverse('edit_milestone', args=(3,)), context, follow=True)
        self.assertEqual('Milestone with given title already exists', response.context['error_message'])

    def test_delete_milestone_succeful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        size_before = len(Milestone.objects.all())
        self.client.post(reverse('delete_milestone', args=(1,)), context, follow=True)
        self.assertTrue(size_before > len(Milestone.objects.all()))

    def test_delete_milestone_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user2'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.post(reverse('delete_milestone', args=(1,)), context, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_get_contributors(self):
        project1 = Project.objects.get(id=1)
        self.assertEqual(len(project1.get_contributors()), 2)
        self.assertEqual(project1.get_contributors()[0].username, 'user4')
        self.assertEqual(project1.get_contributors()[1].username, 'user5')

        project2 = Project.objects.get(id=2)
        self.assertEqual(len(project2.get_contributors()), 1)
        self.assertEqual(project2.get_contributors()[0].username, 'user6')

        project3 = Project.objects.get(id=3)
        self.assertEqual(len(project3.get_contributors()), 0)

    def test_get_noncontributors(self):
        project1 = Project.objects.get(id=1)
        non_contributors_size = len(GitUser.objects.all()) - len(project1.get_contributors()) - 1
        self.assertEqual(non_contributors_size, len(project1.get_noncontributors()))
        self.assertTrue('user4' not in project1.get_noncontributors())
        self.assertTrue('user5' not in project1.get_noncontributors())

        project2 = Project.objects.get(id=2)
        non_contributors_size = len(GitUser.objects.all()) - len(project2.get_contributors()) - 1
        self.assertEqual(non_contributors_size, len(project2.get_noncontributors()))
        self.assertTrue('user6' not in project2.get_noncontributors())

    def test_add_file_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'New title', 'new_text': 'New text for a file'}
        branch = Branch.objects.get(id=2)
        size_before = len(File.objects.filter(branch=branch))
        self.client.post(reverse('add_file', args=(2,)), context, follow=True)
        self.assertTrue(len(File.objects.filter(branch=branch)) > size_before)

        context = {'new_title': 'File 2', 'new_text': 'New text for a file'}
        branch = Branch.objects.get(id=2)
        size_before = len(File.objects.filter(branch=branch))
        self.client.post(reverse('add_file', args=(2,)), context, follow=True)
        self.assertTrue(len(File.objects.filter(branch=branch)) > size_before)

    def test_add_file_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '  ', 'new_text': 'New text for a file'}
        response = self.client.post(reverse('add_file', args=(2,)), context, follow=True)
        self.assertEqual('File title can\'t be empty', response.context['error_message'])

        context = {'new_title': 'File 1', 'new_text': 'New text for a file'}
        response = self.client.post(reverse('add_file', args=(2,)), context, follow=True)
        self.assertEqual('File with given title already exists', response.context['error_message'])

    def test_edit_file_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'New title', 'new_text': 'New text for a file'}
        file_before = File.objects.get(id=3)
        self.client.post(reverse('edit_file', args=(3,)), context, follow=True)
        file_after = File.objects.get(id=3)
        self.assertNotEqual(file_before.title, file_after.title)
        self.assertNotEqual(file_before.text, file_after.text)

        context = {'new_title': 'File 2', 'new_text': 'Generic text for file 2'}
        file_before = File.objects.get(id=3)
        self.client.post(reverse('edit_file', args=(3,)), context, follow=True)
        file_after = File.objects.get(id=3)
        self.assertNotEqual(file_before.title, file_after.title)
        self.assertNotEqual(file_before.text, file_after.text)

    def test_edit_file_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '  ', 'new_text': 'New text for a file'}
        response = self.client.post(reverse('edit_file', args=(1,)), context, follow=True)
        self.assertEqual('File title can\'t be empty', response.context['error_message'])

        context = {'new_title': 'File 6', 'new_text': 'New text for a file'}
        response = self.client.post(reverse('edit_file', args=(1,)), context, follow=True)
        self.assertEqual('File with given title already exists', response.context['error_message'])

    def test_delete_file(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        branch = Branch.objects.get(id=1)
        size_before = len(File.objects.filter(branch=branch))
        self.client.post(reverse('delete_file', args=(2,)), context, follow=True)
        self.assertTrue(len(File.objects.filter(branch=branch)) < size_before)

    def test_contributors_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.post(reverse('contributors', args=(1,)), context, follow=True)
        self.assertEqual(len(response.context['contributors']), 2)
        self.assertEqual(len(response.context['other_users']), 4)

    def test_contributors_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user2'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.post(reverse('contributors', args=(1,)), context, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_add_contributor_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        project = Project.objects.get(id=1)
        size_before = len(project.get_contributors())
        context = {'new_contributor': 'user2'}
        self.client.post(reverse('add_contributor', args=(1,)), context, follow=True)
        project = Project.objects.get(id=1)
        self.assertTrue(len(project.get_contributors()) > size_before)

    def test_add_contributor_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user2'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_contributor': 'user6'}
        response = self.client.post(reverse('add_contributor', args=(1,)), context, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_remove_contributor_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        project = Project.objects.get(id=1)
        size_before = len(project.get_contributors())
        self.client.post(reverse('remove_contributor', args=(1, 'user4', )), context, follow=True)
        project = Project.objects.get(id=1)
        self.assertTrue(len(project.get_contributors()) < size_before)

    def test_remove_contributor_unsuccessful(self):
        context = {'uname': 'user2', 'psw': 'user2'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        response = self.client.post(reverse('remove_contributor', args=(1, 'user4',)), context, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_comments(self):
        project = Project.objects.get(id=1)
        comments1 = project.get_comments('user1')
        comments2 = project.get_comments('user4')

        self.assertEqual(len(comments1), len(comments2))
        self.assertNotEqual(comments2[0]['reaction'], comments1[0]['reaction'])

        self.assertEqual(comments1[0]['reaction'], '')
        self.assertEqual(comments1[1]['reaction'], 'LIKE')
        self.assertEqual(comments1[2]['reaction'], 'DISLIKE')

    def test_add_comment_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        project = Project.objects.get(id=1)
        context = {'new_comment': 'Generic new comment'}
        size_before = len(project.get_comments('user1'))
        self.client.post(reverse('add_comment', args=(1, )), context, follow=True)
        self.assertTrue(len(project.get_comments('user1')) > size_before)
        self.assertEqual(project.get_comments('user1')[0]['comment'].text, 'Generic new comment')

    def test_add_comment_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_comment': '   '}
        response = self.client.post(reverse('add_comment', args=(1, )), context, follow=True)
        self.assertEqual(response.context['error_message'], 'You can\'t submit an empty comment')

    def test_toggle_reaction(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        user = GitUser.objects.get_by_natural_key("user1")
        comment = Comment.objects.get(id=1)

        # testing adding
        size_before = len(Reaction.objects.filter(user=user, comment=comment))
        self.client.post(reverse('toggle_reaction', args=(1, 'LIKE', )), context, follow=True)
        self.assertTrue(len(Reaction.objects.filter(user=user, comment=comment)) > size_before)

        # testing changing
        reaction_before = Reaction.objects.filter(user=user, comment=comment)[0].type
        self.client.post(reverse('toggle_reaction', args=(1, 'DISLIKE',)), context, follow=True)
        self.assertNotEqual(Reaction.objects.filter(user=user, comment=comment)[0].type, reaction_before)

        # testing deleting
        size_before = len(Reaction.objects.filter(user=user, comment=comment))
        self.client.post(reverse('toggle_reaction', args=(1, 'DISLIKE',)), context, follow=True)
        self.assertTrue(len(Reaction.objects.filter(user=user, comment=comment)) < size_before)

    def test_get_all_participants(self):
        project = Project.objects.get(id=1)
        participants = project.get_all_participants()

        self.assertEqual(len(participants), 3)
        self.assertTrue(len(participants) > len(project.get_contributors()))

        self.assertEqual(participants[0], 'user4')
        self.assertEqual(participants[1], 'user5')
        self.assertEqual(participants[2], 'user1')

    def test_project_can_edit(self):
        project = Project.objects.get(id=1)

        self.assertTrue(project.can_edit('user1'))
        self.assertTrue(project.can_edit('user4'))
        self.assertFalse(project.can_edit('user2'))

    def test_project_get_issues(self):
        project = Project.objects.get(id=1)
        open = project.get_issues('OPEN')
        closed = project.get_issues('CLOSED')

        self.assertEqual(len(open), 3)
        self.assertEqual(len(closed), 2)

    def test_milestone_get_issues(self):
        milestone = Milestone.objects.get(id=1)
        open = milestone.get_issues('OPEN')
        closed = milestone.get_issues('CLOSED')

        self.assertEqual(len(open), 2)
        self.assertEqual(len(closed), 1)

    def test_get_percent(self):
        milestone = Milestone.objects.get(id=1)
        self.assertEqual(milestone.get_percent(), 33)

        milestone = Milestone.objects.get(id=2)
        self.assertEqual(milestone.get_percent(), 100)

        milestone = Milestone.objects.get(id=3)
        self.assertEqual(milestone.get_percent(), 0)

    def test_add_issue_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        project_size_before = len(Project.objects.get(id=1).get_issues('OPEN'))
        milestone_size_before = len(Milestone.objects.get(id=1).get_issues('OPEN'))
        context = {'new_title': 'new_title', 'new_desc': 'new_desc', 'assignee': 'user1', 'milestone': 'Milestone 1'}
        self.client.post(reverse('add_issue', args=(1, )), context, follow=True)
        self.assertTrue(len(Project.objects.get(id=1).get_issues('OPEN')) > project_size_before)
        self.assertTrue(len(Milestone.objects.get(id=1).get_issues('OPEN')) > milestone_size_before)

        project_size_before = len(Project.objects.get(id=1).get_issues('OPEN'))
        milestone_size_before = len(Milestone.objects.get(id=1).get_issues('OPEN'))
        context = {'new_title': 'new_title 2', 'new_desc': 'new_desc', 'assignee': 'None', 'milestone': 'None'}
        self.client.post(reverse('add_issue', args=(1, )), context, follow=True)
        self.assertTrue(len(Project.objects.get(id=1).get_issues('OPEN')) > project_size_before)
        self.assertTrue(len(Milestone.objects.get(id=1).get_issues('OPEN')) == milestone_size_before)

    def test_add_issue_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '   ', 'new_desc': 'new_desc', 'assignee': 'None', 'milestone': 'None'}
        response = self.client.post(reverse('add_issue', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Title can\'t be empty')

        context = {'new_title': 'Issue 1', 'new_desc': 'new_desc', 'assignee': 'None', 'milestone': 'None'}
        response = self.client.post(reverse('add_issue', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Issue with given title already exists')

    def test_edit_issue_successful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'new_title', 'new_desc': 'new_desc', 'assignee': 'user4', 'milestone': 'Milestone 3'}
        self.client.post(reverse('edit_issue', args=(1,)), context, follow=True)
        issue = Issue.objects.get(id=1)
        self.assertEqual(issue.title, 'new_title')
        self.assertEqual(issue.description, 'new_desc')
        self.assertEqual(issue.assignee.username, 'user4')
        self.assertEqual(issue.milestone.title, 'Milestone 3')

        context = {'new_title': 'new_title', 'new_desc': '', 'assignee': 'None', 'milestone': 'None'}
        self.client.post(reverse('edit_issue', args=(1,)), context, follow=True)
        issue = Issue.objects.get(id=1)
        self.assertEqual(issue.title, 'new_title')
        self.assertEqual(issue.description, '')
        self.assertIsNone(issue.assignee)
        self.assertIsNone(issue.milestone)

    def test_edit_issue_unsuccessful(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': '   ', 'new_desc': 'new_desc', 'assignee': 'user4', 'milestone': 'Milestone 3'}
        response = self.client.post(reverse('edit_issue', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Title can\'t be empty')

        context = {'new_title': 'Issue 3', 'new_desc': '', 'assignee': 'None', 'milestone': 'None'}
        response = self.client.post(reverse('edit_issue', args=(1,)), context, follow=True)
        self.assertEqual(response.context['error_message'], 'Issue with given title already exists')

    def test_toggle_issue_status(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        # test closing
        self.assertEqual(Issue.objects.get(id=1).state, 'OPEN')
        percentage_before = Issue.objects.get(id=1).milestone.get_percent()
        self.client.post(reverse('toggle_issue', args=(1,)), context, follow=True)
        self.assertEqual(Issue.objects.get(id=1).state, 'CLOSED')
        self.assertTrue(Issue.objects.get(id=1).milestone.get_percent() > percentage_before)

        # test reopening
        percentage_before = Issue.objects.get(id=1).milestone.get_percent()
        self.client.post(reverse('toggle_issue', args=(1,)), context, follow=True)
        self.assertEqual(Issue.objects.get(id=1).state, 'OPEN')
        self.assertTrue(Issue.objects.get(id=1).milestone.get_percent() < percentage_before)

    def test_get_commits(self):
        branch = Branch.objects.get(id=1)

        commits = branch.get_commits()
        self.assertEqual(commits[0].log_message, 'File File 6 added')
        self.assertEqual(commits[0].log_message, 'File File 2 added')
        self.assertEqual(commits[0].log_message, 'File File 1 added')

    def test_get_add_file_commit(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'New title', 'new_text': 'New text for a file'}
        size_before = len(Branch.objects.get(id=2).get_commits())
        self.client.post(reverse('add_file', args=(2,)), context, follow=True)
        branch = Branch.objects.get(id=2)
        self.assertTrue(len(branch.get_commits()) > size_before)
        self.assertEqual(branch.get_commits()[0].log_message, 'File New title added')

    def test_get_edit_file_commit(self):
        context = {'uname': 'user4', 'psw': 'user4'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        context = {'new_title': 'New title', 'new_text': 'New text for a file'}
        self.client.post(reverse('edit_file', args=(1,)), context, follow=True)
        commit = Branch.objects.get(id=1).get_commits()[0]
        self.assertEqual(commit.log_message, 'File File 1 changed')
        self.assertEqual(commit.committer, 'user4')

    def test_delete_file_commit(self):
        context = {'uname': 'user1', 'psw': 'user1'}
        self.client.post('http://localhost:8000/login/', context, follow=True)

        size_before = len(Branch.objects.get(id=1).get_commits())
        self.client.post(reverse('delete_file', args=(1,)), context, follow=True)
        branch = Branch.objects.get(id=1)
        self.assertTrue(len(branch.get_commits()) > size_before)
        self.assertEqual(branch.get_commits()[0].log_message, 'File File 1 deleted')
