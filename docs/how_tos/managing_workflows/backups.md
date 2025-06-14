# Backups

We recommend that you regularly backup important workflows in case something happens to the
database server.

## Arango tools

Arango provides `arangodump` and `arangorestore`. These are the most robust tools and are
recommended for backup if you have direct access to the database.

Refer to {ref}`arango-tool-installation` for installation instructions.

Replace `<your-database-name>` and `<your-database-hostname>` with correct names in the
commands below.

### Docker container

#### Dump

```console
$ docker run -it arangodb/arangodb:latest arangodump \
    --server.database <your-database-name> \
    --output-directory dump \
    --compress-output false \
    --include-system-collections true \
    --server.endpoint "http+tcp://<your-database-hostname>:8529"
```

#### Restore

```console
$ docker run -it arangodb/arangodb:latest arangorestore \
    --server.database <your-database-name> \
    --create-database \
    --input-directory dump \
    --include-system-collections true \
    --server.endpoint "http+tcp://<your-database-hostname>:8529"
```

### Apptainer container on Kestrel

#### Dump

```console
$ apptainer run /datasets/images/arangodb/arangodb.sif \
    arangodump \
    --server.database \
    <your-database-name> \
    --output-directory dump \
    --compress-output false \
    --include-system-collections true \
    --server.endpoint "http+tcp://<your-database-hostname>:8529"
```

#### Restore

```console
$ apptainer run /datasets/images/arangodb/arangodb.sif \
    arangorestore \
    --server.database <your-database-name> \
    --create-database \
    --input-directory dump \
    --server.endpoint "http+tcp://<your-database-hostname>:8529"
```

## SQLite

You can export your workflows to a SQLite file with the command below. There is currently no
support for restoring from the file, but we will eventually add it.

```console
$ torc export sqlite
```

## Workflow Specification

You can convert your workflow to a torc worklow specification with the command below. Redirect the
text to a file to save it. Then you can re-create it later with the `create-from-json-file`
command.

```{eval-rst}
.. warning:: This command may not work if the size of you worklow is greater than what can be
   transferred in an HTTP API command.
```

```console
$ torc workflows show
```
