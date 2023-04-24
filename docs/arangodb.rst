########
ArangoDB
########
Torc relies heavily on the multi-model database `ArangoDB <https://www.arangodb.com/>`_.
It uses graphs to store relationships/dependencies between workflow objects and documents
for user-defined data.

Torc provides a moderately-comprehensive set of CLI commands and a custom HTTP API endpoint with
auto-generated client API libraries. The goal is for users to not be forced to deal with ArangoDB
directly, but there are still cases where that may be required. The web UI is particularly
beneficial for useful for running queries, visualizing workflow graphs, and making minor edits to
documents..
``arangodump/arangorestore`` are great for backups.

Here are documentation links for some of their tools:

- Web UI: https://www.arangodb.com/docs/stable/programs-web-interface.html
- Queries: https://www.arangodb.com/docs/stable/programs-web-interface-aql-editor.html
- Shell: https://www.arangodb.com/docs/stable/programs-arangosh.html
- Export: https://www.arangodb.com/docs/stable/programs-arangoexport.html
- Backups: https://www.arangodb.com/docs/stable/programs-arangodump.html
- HTTP API: https://www.arangodb.com/docs/stable/http/
