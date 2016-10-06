import os
import yaml
from termcolor import colored


def get_config(config_path=None):
    """
    Loads configuration from yaml file
    """
    if not config_path:
        config_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ), 'config.yml')

    if not os.path.exists(config_path):
        print colored("Error: ", "red") + " config path not found %s" % config_path
        exit()

    with file(config_path) as stream:
        return yaml.load(stream)


def create_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            raise exception


def open_file(path):
    if not os.path.exists(path):
        return None

    with file(path) as f:
        content = f.read()

    return content


class FileLock(object):
    @staticmethod
    def get(path):
        return open_file(path)

    @staticmethod
    def save(path, value):
        with open(path, 'r+') as _file:
            _file.write(value)


    @staticmethod
    def delete(path, value):
        raise Exception("Method not implemented")