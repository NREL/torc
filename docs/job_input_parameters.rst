####################
Job Input Parameters
####################

There are two options for running jobs with input parameters.

CLI Commands
============
Jobs are CLI commands where input and output parameters are defined as command-line parameters. The
user adds one job for each permutation of commands, arguments, and options.

Database
========
Users store job input parameters in ``user_data`` collections in the database and then the job
script send API calls to retrieve them at runtime.
