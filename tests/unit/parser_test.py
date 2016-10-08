import unittest2
from sqlupdater.parser import HiveDatabaseParser


class HiveDatabaseParserTest(unittest2.TestCase):
    def test_parsing_database_name(self):
        _input = [
            'create table database.table',
            'create external table if exists database.table',
            'crete table table',
            'create something something'
        ]

        output = [
            ['database', 'table'],
            ['database', 'table'],
            None,
            None
        ]

        parser = HiveDatabaseParser()
        for item in xrange(0, 3):
            try:
                self.assertEqual(output[item], parser.parse(_input[item]))
            except ValueError, e:
                self.assertIsNone(output[item])
