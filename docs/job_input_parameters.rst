####################
Job Input Parameters
####################
In all cases the database requires that each job have a unique name. If this is not natural for
some use cases then we can make a helper script to generate unique names.

CLI Commands
============
Jobs are CLI commands where input and output parameters are defined as command-line parameters. The
user adds one job for each permutation of commands, arguments, and options.

Database
========
User stores input parameters for each job in the database. Each job has a unique name and can be
retrieved in the API with it. When a job starts it sends an HTTP GET request to read its inputs.
