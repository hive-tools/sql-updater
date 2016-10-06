# sql-updater

This project aims to help you to organize your database structure in an easy way. We want to give you the power from Git as version control to versioning your databases and tables.

### Example of usage

cli.py accepts 3 parameters:

- `-s --show` allows you to display latest changes in your Git repo without executing the queries.
- `-e --execute` executes all the new changes
- `-p --project` define which project you want to work

### Config example

```yml
---
metadata_path: /path_to_my_metadata/
projects:
  hive_project:
      name: main_hive_cluster
      backend: hive
      repo: git@github.com:ssola/test-data.git
      filters:
        only_sql_files:
          filter: file_type
          types:
            - ".sql"
```

With this example we are defining a project called `hive_project` that it's using `hive` backend to update all the queries stored in the repo `git@github.com:ssola/test-data.git`. Because we are only intested in sql files we are defining the filter. This filters cleans up the list of updated files deleting any file which extension isn't `.sql`
