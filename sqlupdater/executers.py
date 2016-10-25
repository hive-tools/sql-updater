import re, os
import json
import commands
from termcolor import colored
from sqlupdater.parser import HiveDatabaseParser
from sqlupdater.utils import open_file, FileLock


class Executor(object):
    def update_lock(self, project):
        current_commit = str(project.repo.head.commit)
        working_dir = project.repo.working_dir
        file_name = os.path.join(os.path.dirname(working_dir), '.commit_lock')
        FileLock.save(file_name, current_commit)

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


class CacheInterface(object):
    def set_item(self, keu, value):
        raise Exception("Method not implemented")

    def remove_item(self, key, item):
        raise Exception("Method not implemented")

    def update_item(self, keu, value):
        raise Exception("Method not implemented")

    def get_item(self, key):
        raise Exception("Method not implemented")

    def has_item(self, key):
        raise Exception("Method not implemented")

    def set_value_in_item(self, key, item):
        raise Exception("Method not implemented")

    def store(self, path):
        raise Exception("Method not implemented")


class CacheData(CacheInterface):
    def __init__(self, project):
        self._data = {}
        self._project = project
        working_dir = project.repo.working_dir
        file_path = os.path.join(os.path.dirname(working_dir), '.db_cache')
        self._path = file_path
        self._data = self._get_data()

    def _get_data(self):
        if not os.path.exists(self._path):
            return {}

        _cached_data = open_file(self._path)
        if not _cached_data:
            return {}

        return json.loads(open_file(self._path))

    def set_item(self, key, value):
        self._data[key] = value

    def set_value_in_item(self, key, item):
        if self.has_item(key):
            self._data[key] += [item]

    def remove_item(self, key, item):
        if self.has_item(key):
            if item in self._data[key]:
                self._data[key].remove(item)

    def update_item(self, key, value):
        self.remove_item(key)
        self.set_item(key, value)

    def get_item(self, key):
        if key not in self._data:
            return None

        return self._data[key]

    def has_item(self, key):
        if key not in self._data:
            return False
        return True

    def __del__(self):
        data = json.dumps(self._data)
        with open(self._path, 'w+') as _file:
            _file.write(data)


class HiveClient(object):
    PARSE_DATA_REGEX = "OK\\n([a-zA-Z0-9_\\n]+)\\nTime"

    def __init__(self, cache):
        self._cache = cache

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

        if len(items) > 0:
            return items[0].split("\n")

        return []

    def get_databases(self):
        if self._cache.has_item("databases"):
            return self._cache.get_item("databases")

        output = self._execute_command("sudo -u mapr hive -e \"SHOW "
                                       "DATABASES\"", True)

        databases = self._get_items_from_output(output)
        self._cache.set_item("databases", databases)

        return databases

    def create_database(self, database):
        if self._execute_command("sudo -u mapr hive -e \"CREATE "
                                     "DATABASE IF NOT EXISTS %s\""
                                     % database):
            self._cache.set_value_in_item("databases", database)
            return True

        return False

    def get_tables(self, database):
        key = "{}_tables".format(database)

        if self._cache.has_item(key):
            return self._cache.get_item(key)

        output = self._execute_command("sudo -u mapr hive -e \"USE %s; "
                                       "SHOW TABLES;\"" % database, True)

        tables = self._get_items_from_output(output)
        self._cache.set_item(key, tables)

        return tables

    def create_table_from_file(self, file_path, database, table):
        if self._execute_command("sudo -u mapr hive -f %s" % file_path):
            key = "{}_tables".format(database)
            self._cache.set_value_in_item(key, table)
            return True

        return False

    def drop_table(self, database, table):
        if self._execute_command("sudo -u mapr hive -e \"USE %s; DROP "
                                     "TABLE %s;\"" % (database, table)):
            key = "{}_tables".format(database)
            if self._cache.has_item(key):
                self._cache.remove_item(key, table)

            return True

        return False

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

            if not self._database_exists(database):
                if self._hive_client.create_database(database):
                    print colored("Database %s created" % database, "green")
                else:
                    print colored("Was an error creating database %s" %
                                  database, "red")
            else:
                print "Database %s already exists" % database

            if table in self._hive_client.get_tables(database):
                if self._hive_client.drop_table(database, table):
                    print "Table %s.%s dropped successfully" % (database,
                                                                table)
            if self._hive_client.create_table_from_file(query_file,
                                                        database, table):
                print "Table %s.%s created successfully" % (database, table)
            if self._hive_client.repair_table(database, table):
                print "Table %s.%s repaired successfully" % (database, table)
        except ValueError, e:
            print colored("Content not valid", "red")
            raise
        except Exception, e:
            raise e

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
                        #   self.update_lock(project)
                    except ValueError, e:
                        raise e
        else:
            print 'Everything up to date'
