import re
import commands
from termcolor import colored
from sqlupdater.parser import HiveDatabaseParser
from sqlupdater.utils import open_file


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


class HiveClient(object):
    PARSE_DATA_REGEX = "OK\\n([a-zA-Z_\\n]+)\\nTime"

    def _execute_command(self, command, return_output=False):
        output = commands.getstatusoutput(command)

        if output[0] == 0:
            if return_output:
                return output[1]
            return True
        else:
            raise Exception(output[1])

    def _get_items_from_output(self, output):
        items = re.findall(self.PARSE_DATA_REGEX, output)

        if len(items[0]) > 0:
            return items[0].split("\n")

        return []

    def get_databases(self):
        output = self._execute_command("sudo -u mapr hive -e \"SHOW "
                                       "DATABASES\"", True)

        return self._get_items_from_output(output)

    def create_database(self, database):
        return self._execute_command("sudo -u mapr hive -e \"CREATE "
                                          "DATABASE IF NOT EXISTS %s\""
                                          % database)

    def get_tables(self, database):
        output = self._execute_command("sudo -u mapr hive -e \"USE %s; "
                                          "SHOW TABLES;\"" % database, True)

        return self._get_items_from_output(output)

    def create_table_from_file(self, file_path):
        return self._execute_command("sudo -u mapr hive -f %s" % file_path)

    def drop_table(self, database, table):
        return self._execute_command("sudo -u mapr hive -e \"USE %s; DROP "
                                     "TABLE %s;\"" % (database, table))

    def drop_database(self, database):
        return self._execute_command("sudo -u mapr hive -e \"DROP DATABASE "
                                     "%s;\"" % database)

    def repair_table(self, database, table):
        return self._execute_command("sudo -u mapr hive -e \"USE %s; "
                                          "MSCK REPAIR TABLE %s\"" % (
                                            database, table))


class HiveExecutor(Executor):
    def __init__(self, hive_client):
        self._hive_client = hive_client

    def _database_exists(self, database):
        if database in self._hive_client.get_databases():
            return True
        else:
            return False

    def _create_tables(self, buffer, query_file):
        parser = HiveDatabaseParser()

        try:
            (database, table) = parser.parse(buffer)
            print "Check if database %s exists to create table %s" % (
                database, table)

            if not self._database_exists(database):
                if self._hive_client.create_database(database):
                    print colored("Database %s created" % database, "green")
                else:
                    print colored("Was an error creating database %s" %
                                  database, "red")
            else:
                print "Database %s already exists" % database

            if table in self._hive_client.get_tables(database):
                self._hive_client.drop_table(database, table)

            self._hive_client.create_table_from_file(query_file)
            self._hive_client.repair_table(database, table)
        except ValueError, e:
            print colored("Content not valid", "red")
            raise
        except Exception, e:
            print e

    def execute(self, project):
        modified_files = project.diff()

        if modified_files:
            print '%d files has been modified' % len(modified_files)

            for _file in modified_files:
                if _file.change_type in ['D', 'M']:
                    word = 'New' if _file.change_type == 'D' else 'Modified'
                    print "- %s " % word + colored(_file.file_path, "green")

                    buffer = open_file(_file.file_path)

                    try:
                        self._create_tables(buffer, _file.file_path)
                    except ValueError, e:
                        pass