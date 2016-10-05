from termcolor import colored


class Executor(object):
    def execute(self, project):
        raise Exception("Method not implemented")


class DummyExecutor(Executor):
    def execute(self, project):
        modified_files = project.diff()

        if modified_files:
            print '%d files has been modified' % len(modified_files)
            for _file in modified_files:
                if _file.change_type in ['D', 'M']:
                    word = 'New' if _file.change_type == 'D' else 'Modified'
                    print "- %s " % word + colored(_file.file_path, "green")
                elif _file.change_type in ['A']:
                    print "- Deleted " + colored(_file.file_path, "red")
        else:
            print 'Nothing has changed'