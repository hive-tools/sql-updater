# sql-updater [![Build Status](https://travis-ci.org/ssola/sql-updater.svg?branch=master)](https://travis-ci.org/ssola/sql-updater)

This project aims to help you to organize your database structure in an easy way. We want to give you the power from Git as a version control to versioning your databases and tables structure.

With this tool every new commit in your project repo means a new query should be executed, but with the Git history of commits we are going to execute the minimal and necessary queries.

![creting new table](http://i.imgur.com/Icb90pI.gif)

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

### Supported Backends

#### Hive

We support to create databases and tables in Hive. With this tool everytime you execute a query we are going to check if the database exists before to execute your query (otherwise it will fail).

If table already exists we are going to drop it and create it again. After all the process we repair your tables, so you don't have to care about adding the `MSCK REPAIR` command in every single file.

### Philosophy

At the moment we only support `hive` as backend service to update our queries. But it's quite straightforward to extend it to numerous backends. 

We use classes called `Executors`. Basically depending which backend are you going to run your project we can select a differet executor to execute the tasks. 

Currently we only have the HiveExecutor with the HiveClient. But if we need to do the same for MySQL we have to code our own MySQLExecutor and we are done.

Then we have something called `Filters` that help us to clean up the final list of tasks to execute. At this time we only implemented the `FileExtensionFilter`, but as you can imagine it's quite easy to create new ones following the `Filter` contract.

### TODO

- [ ] Write tests
- [x] Clean up the code a little bit
- [ ] Create `-h --help` parameter
- [ ] Init project with a specific commit
- [ ] Implement for real filters from project configuration
- [x] Caching layer
