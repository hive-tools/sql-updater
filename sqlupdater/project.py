import os
from sqlupdater.utils import create_dir, FileLock
from sqlupdater.filters import FileExtensionFilter
from git import Repo, GitCommandError
from termcolor import colored


class FileChanged(object):
    def __init__(self, change_type, file_path):
        self._change_type = change_type
        self._file_path = file_path

    @property
    def change_type(self):
        return self._change_type

    @property
    def file_path(self):
        return self._file_path

    def __eq__(self, other):
        return True if self._change_type == other.change_type \
                and self._file_path == other.file_path else False


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

            modified_files = map(
                lambda x:  FileChanged(x.change_type, os.path.join(
                    self.repo.working_dir, x.a_path)),
                diff_index
            )

        _filter = FileExtensionFilter()
        modified_files = filter(
            lambda x: _filter.do_filter(x, ['.sql']), modified_files
        )

        return modified_files

    @property
    def repo(self):
        return Repo(os.path.join(self._project_dir, 'repo'))