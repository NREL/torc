###############
User Strategies
###############

CLI Commands
============
Job are CLI commands where input and output parameters are defined as command-line parameters.

API-Driven
==========
User stores input parameters for each job in the database. When a job starts it sends an HTTP GET
request to read its inputs.


