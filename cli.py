import argparse
import os
from sqlupdater.utils import create_dir, get_config
from sqlupdater.project import Project
from sqlupdater.executers import DummyExecutor


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


def setup_project(config, project_name):
    """
    Updates or setup a new project and return the Repo.
    """
    create_dir(config['metadata_path'])

    if project_name not in config['projects']:
        raise Exception('Project not found %s' % project_name)

    project_config = config['projects'][project_name]
    project_dir = os.path.join(config['metadata_path'], project_name)
    project = Project(project_dir, project_config)
    project.init_project()

    return project


def main():
    args = get_args()

    # load config
    config = get_config()
    project_name = args.project
    project = setup_project(config, project_name)

    if args.show:
        executor = DummyExecutor()
        executor.execute(project)

main()
