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

### Philosophy

At the moment we only support `hive` as backend service to update our queries. But it's quite straightforward to extend it to numerous backends. 

We use classes called `Executors`. Basically depending which backend are you going to run your project we can select a differet executor to execute the tasks. 

Currently we only have the HiveExecutor with the HiveClient. But if we need to do the same for MySQL we have to code our own MySQLExecutor and we are done.

Then we have something called `Filters` that help us to clean up the final list of tasks to execute. At this time we only implemented the `FileExtensionFilter`, but as you can imagine it's quite easy to create new ones following the `Filter` contract.

### TODO

- [ ] Write tests
- [ ] Clean up the code a little bit
- [ ] Create `-h --help` parameter
- [ ] Init project with a specific commit
