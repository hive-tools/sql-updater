import os


def create_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            raise exception


class FileLock(object):
    @staticmethod
    def get_lock_value(path):
        if not os.path.exists(path):
            return None

        with file(path) as f:
            commit = f.read()

        return commit