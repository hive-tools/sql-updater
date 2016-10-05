import argparse
import os
import yaml
from termcolor import colored
from sqlupdater.utils import create_dir
from sqlupdater.project import Project


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


def setup_project(config, project_name):
    """
    Updates or setup a new project and return the Repo.
    """
    create_dir(config['metadata_path'])

    if project_name not in config['projects']:
        raise Exception('Project not found %s' % project_name)

    project_config = config['projects'][project_name]
    project_dir = os.path.join(config['metadata_path'], project_name)
    project = Project(project_dir)
    project.init_project(project_config)

    return project

def main():
    args = get_args()

    # load config
    config = get_config()
    project_name = args.project
    project = setup_project(config, project_name)

    if args.show:
        modified_files = project.diff()
        if modified_files:
            print '%d files has been modified' % len(modified_files)
            for _file in modified_files:
                if _file["change_type"] in ['D', 'M']:
                    word = 'New' if _file["change_type"] == 'D' else 'Modified'
                    print "- %s " % word + colored(_file["path"], "green")
                elif _file["change_type"] in ['A']:
                    print "- Deleted " + colored(_file["path"], "red")
        else:
            print 'Nothing has changed'


main()
