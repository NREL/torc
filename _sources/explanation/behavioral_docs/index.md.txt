(behavioral-docs)=

# Behavioral Documentation

This section describes what a user will observe when using torc. It describes the following
software components:

- **torc client application**: This is the `torc` CLI command that you run after installing the
  Python `torc` software package.
- **torc worker application**: This is the torc application that runs jobs on compute nodes. You do
  not interact with it directly.
- **torc database service**: This is a torc service installed into each database in an ArangoDB
  instance. It is an API endpoint that provides an interface to manage data in the database.

```{toctree}
:hidden: true
:maxdepth: 3

workflows
jobs
hpc
db_errors
```
