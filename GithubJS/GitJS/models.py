from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class GitUser(User):

    def get_my_projects(self):
        all_projects = Project.objects.all()
        my_projects = []
        for project in all_projects:
            if project.can_edit(self.username):
                my_projects.append(project)
        return my_projects

    def get_starred_projects(self):
        starred_projects = StarredProject.objects.filter(user_id=self.pk)
        starred = []
        for sp in starred_projects:
            starred.append(Project.objects.get(id=sp.project_id))
        return starred

    def add_starred(self, project_id):
        new_starred = StarredProject(project_id=project_id, user_id=self.pk)
        new_starred.save()

    def remove_starred(self, project_id):
        starred = StarredProject.objects.get(project_id=project_id, user_id=self.pk)
        starred.delete()

    def get_watched_changes(self):
        watched_projects = ProjectUpdate.objects.filter(user_id=self.pk).order_by('-up_date')
        return watched_projects

    def add_watched(self, project_id):
        new_watched = WatchedProject(project_id=project_id, user_id=self.pk)
        new_watched.save()

    def remove_watched(self, project_id):
        watched = WatchedProject.objects.get(project_id=project_id, user_id=self.pk)
        watched.delete()


class Project(models.Model):
    title = models.CharField(max_length=100)
    lead = models.ForeignKey(GitUser, on_delete=models.CASCADE)

    def get_branch_number(self):
        branches = Branch.objects.filter(project=self)
        return len(branches)

    def get_branches(self):
        branches = Branch.objects.filter(project=self)
        return branches

    def update_users(self, message):
        for watched in WatchedProject.objects.filter(project_id=self.id):
            new_date = timezone.now()
            update = ProjectUpdate(project_id=self.id, user_id=watched.user_id, up_date=new_date, message=message)
            update.save()

    def get_milestones(self, state):
        milestones = Milestone.objects.filter(project=self, state=state)
        return milestones

    def get_issues(self, state):
        issues = Issue.objects.filter(project=self, state=state)
        return issues

    def get_pull_requests(self, state):
        pull_requests = []
        if state == 'OPEN':
            pull_requests = PullRequest.objects.filter(project=self, state=state)
        else:
            all_requests = PullRequest.objects.filter(project=self)
            for req in all_requests:
                if req.state == 'CLOSED' or req.state == 'MERGED':
                    pull_requests.append(req)
        return pull_requests

    def get_contributors(self):
        contributors = Contributor.objects.filter(project_id=self.id)
        return contributors

    def get_noncontributors(self):
        ret = []
        for con in GitUser.objects.all():
            if self.lead.username != con.username and \
             len(Contributor.objects.filter(username=con.username, project_id=self.id)) == 0:
                ret.append(con.username)
        return ret

    def get_all_participants(self):
        participants = []
        for contributor in self.get_contributors():
            participants.append(contributor.username)
        participants.append(self.lead.username)
        return participants

    def can_edit(self, username):
        for participant in self.get_all_participants():
            if participant == username:
                return True
        return False

    def get_comments(self, username):
        comments = Comment.objects.filter(project=self).order_by('-last_update')
        ret = []
        for comment in comments:
            user = GitUser.objects.get_by_natural_key(username)
            reaction = Reaction.objects.filter(comment=comment, user=user)
            if len(reaction) == 0:
                ret.append({"comment": comment, "reaction": ""})
            else:
                ret.append({"comment": comment, "reaction": reaction[0].type})
        return ret


class StarredProject(models.Model):
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class WatchedProject(models.Model):
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class Contributor(models.Model):
    project_id = models.BigIntegerField()
    username = models.CharField(max_length=100)


class ProjectUpdate(models.Model):
    up_date = models.DateTimeField("date updated")
    message = models.CharField(max_length=100)
    project_id = models.BigIntegerField()
    user_id = models.BigIntegerField()


class Branch(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def get_commits(self):
        commits = Commit.objects.filter(branch=self).order_by('-date_time')
        return commits

    def get_files(self):
        files = File.objects.filter(branch=self)
        return files

    def get_file_by_title(self, title):
        found = File.objects.filter(branch=self, title=title)
        if len(found) == 0:
            return None
        return found[0]


class Milestone(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    due_date = models.DateTimeField("due date")
    state = models.CharField(max_length=7)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def get_issues(self, state):
        issues = Issue.objects.filter(milestone=self, state=state)
        return issues

    def get_percent(self):
        completed = len(Issue.objects.filter(milestone=self, state='CLOSED'))
        total = len(Issue.objects.filter(milestone=self))
        return int(round((completed * 100) / total, 2)) if total != 0 else 0


class File(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=200)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.CharField(max_length=200)
    last_update = models.DateTimeField("last update")
    user = models.ForeignKey(GitUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Reaction(models.Model):
    type = models.CharField(max_length=10)
    user = models.ForeignKey(GitUser, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


class Issue(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    state = models.CharField(max_length=7)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, null=True, on_delete=models.SET_NULL)
    assignee = models.ForeignKey(GitUser, null=True, on_delete=models.SET_NULL)


class Commit(models.Model):
    log_message = models.CharField(max_length=200)
    date_time = models.DateTimeField("date committed")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    committer = models.CharField(max_length=100)


class PullRequest(models.Model):
    state = models.CharField(max_length=7)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, null=True, on_delete=models.SET_NULL)
    source = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, related_name='source')
    target = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL, related_name='target')

    def get_differences(self):
        different_files = self.source.get_files()
        differences = []
        for different in different_files:
            if self.target.get_file_by_title(different.title):
                target_file = self.target.get_file_by_title(different.title)
                differences.append([target_file.text, different.text])
            else:
                differences.append(['', different.text])
        return differences

    def merge_branches(self):
        source_files = self.source.get_files()
        new_files = []
        new_id = File.objects.all().order_by('-id')[0].id + 1
        for file in source_files:
            if self.target.get_file_by_title(file.title):
                changed = File.objects.get(title=file.title, branch=self.target)
                changed.text = file.text
                changed.save()
            else:
                new_file = File(id=new_id, title=file.title, text=file.text, branch=self.target)
                new_files.append(new_file)
                new_id += 1
        File.objects.bulk_create(new_files)
