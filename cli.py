import argparse
import os
import yaml
from termcolor import colored
from git import Repo, GitCommandError


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='Import SQL files')

    parser.add_argument('-s', '--show',
                        required=False,
                        action='store_const',
                        const=True,
                        help='Only show data without executing')

    parser.add_argument('-p', '--project',
                        required=True,
                        action='store',
                        help='Project name')

    return parser


def get_args():
    parser = build_arg_parser()
    return parser.parse_args()


def get_config():
    """
    Loads configuration from yaml file
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')

    with file(config_path) as stream:
        return yaml.load(stream)


def create_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            raise exception


def configure_project(project_dir, config):
    project_dir_git = os.path.join(project_dir, 'repo')

    if not config['repo']:
        raise Exception('Empty repo configuration')

    create_dir(project_dir_git)
    git_path = os.path.join(project_dir_git, '.git')

    if os.path.exists(git_path):
        repo = Repo(project_dir_git)
        print colored('Pulling', 'green') + ' repo %s' % config['repo']
        repo.remotes.origin.pull()
    else:
        try:
            print 'cloning... %s' % config['repo']
            Repo.clone_from(config['repo'], project_dir_git)
        except GitCommandError as e:
            print 'Repo cannot be found'


def setup_project(config, project_name):
    """
    Updates or setup a new project and return the Repo.
    """
    create_dir(config['metadata_path'])

    if project_name not in config['projects']:
        raise Exception('Project not found %s' % project_name)

    project_config = config['projects'][project_name]
    project_dir = os.path.join(config['metadata_path'], project_name)
    configure_project(project_dir, project_config)

    return Repo(os.path.join(project_dir, 'repo'))


def get_lock_commit(path):
    if not os.path.exists(path):
        return None

    with file(path) as f:
        commit = f.read()

    return commit


def has_new_changes(repo):
    current_commit = repo.head.commit
    previous_commit = get_lock_commit(
        os.path.join(os.path.dirname(repo.working_dir), ".commit_lock")
    )

    modified_files = []
    if current_commit != previous_commit:
        index = repo.index
        diff_index = index.diff(previous_commit)

        for diff in diff_index:
            if diff.change_type in ['A', 'M']:
                modified_files += [{
                                       "change_type": diff.change_type,
                                       "path": os.path.join(repo.working_dir, diff.a_path)
                                   }]

    return modified_files


def main():
    args = get_args()

    # load config
    config = get_config()
    project_name = args.project
    project_repo = setup_project(config, project_name)

    if args.show:
        modified_files = has_new_changes(project_repo)
        if modified_files:
            print '%d files has been modified' % len(modified_files)
            for _file in modified_files:
                if _file["change_type"] in ['A', 'M']:
                    print "- " + colored(_file["path"], "green")
        else:
            print 'Nothing has changed'


main()
