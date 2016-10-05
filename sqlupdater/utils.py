import os


def create_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            raise exception

class FileLock(object):
    @staticmethod
    def get(path):
        if not os.path.exists(path):
            return None

        with file(path) as f:
            commit = f.read()

        return commit

    @staticmethod
    def save(path, value):
        raise Exception("Method not implemented")

    @staticmethod
    def delete(path, value):
        raise Exception("Method not implemented")