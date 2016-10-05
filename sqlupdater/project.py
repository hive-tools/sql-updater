import os
from sqlupdater.utils import create_dir, FileLock
from git import Repo, GitCommandError
from termcolor import colored


class Project(object):
    def __init__(self, project_dir, config):
        self._project_dir = project_dir
        self._config = config

    def init_project(self):
        project_dir_git = os.path.join(self._project_dir, 'repo')

        if not self._config['repo']:
            raise Exception('Empty repo configuration')

        create_dir(project_dir_git)
        git_path = os.path.join(project_dir_git, '.git')

        if os.path.exists(git_path):
            repo = Repo(project_dir_git)
            print colored('Pulling', 'green') + ' repo %s' % self._config['repo']
            repo.remotes.origin.pull()
        else:
            try:
                print 'cloning... %s' % self._config['repo']
                Repo.clone_from(self._config['repo'], project_dir_git)
            except GitCommandError as e:
                print 'Repo cannot be found'

    def diff(self, previous_commit=None):
        current_commit = self.repo.head.commit

        if not previous_commit:
            previous_commit = FileLock.get(
                os.path.join(os.path.dirname(self.repo.working_dir), ".commit_lock")
            )

        modified_files = []
        if current_commit != previous_commit:
            index = self.repo.index
            diff_index = index.diff(previous_commit)

            for diff in diff_index:
                modified_files += [{
                                       "change_type": diff.change_type,
                                       "path": os.path.join(self.repo.working_dir, diff.a_path)
                                   }]

        return modified_files

    @property
    def repo(self):
        return Repo(os.path.join(self._project_dir, 'repo'))