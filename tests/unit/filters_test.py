import unittest2
from sqlupdater.filters import FileExtensionFilter
from sqlupdater.project import FileChanged

class FileExtensionFilterTest(unittest2.TestCase):
    def test_filter_by_extension(self):
        _filter = FileExtensionFilter()

        cases = [
            FileChanged('A', 'file.pdf'),
            FileChanged('M', '/documents/images/1.jpeg'),
            FileChanged('D', '/my/queries/query.sql')
        ]

        expected_output = [
            FileChanged('D', '/my/queries/query.sql')
        ]

        output = filter(lambda x: _filter.do_filter(x, ['.sql']), cases)

        self.assertEqual(expected_output, output)