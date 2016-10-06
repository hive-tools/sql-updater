import os


class Filter(object):
    def do_filter(self, file_changed, filter_by=[]):
        raise Exception('Method not implemented')


class FileExtensionFilter(Filter):
    def do_filter(self, file_changed, filter_by=[]):
        extension = os.path.splitext(file_changed.file_path)[1]
        return extension in filter_by
