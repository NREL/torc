(database-installation)=
# ArangoDB instance
Torc requires an instance of [ArangoDB](https://arangodb.com) to store workflow data and serve the Torc API.

If you are at NREL, you can use our shared database (please contact Daniel Thom for access).

If you are not at NREL or want to run your own database, this page provides instructions for deploying
an ArangoDB container.

This is a summary of instructions provided by [ArangoDB](https://arangodb.com/download-major/docker/).

## Start the ArangoDB Docker container

### Ephemeral container
This is the simplest way to run ArangoDB. It will run a container that will be removed when you stop it.
It will not persist data across runs, so you will need to create a new database each time you run it.

```console
$ docker run -p 8529:8529 -e ARANGO_ROOT_PASSWORD=openSesame arangodb/arangodb:3.12.4.3
```

### Persistent container
Create a docker volume to persist data across runs. This uses the name `arangodb-persist`, but you can
use any name you like.
```console
$ docker create --name arangodb-persist arangodb/arangodb:3.12.4.3 true
```

Start the container with that volume.

```console
$ docker run -p 8529:8529 -e ARANGO_ROOT_PASSWORD=openSesame --volumes-from arango-persist arangodb/arangodb:3.12.4.3
```

## Create and configure a database for your workflows

Go to the ArangoDB web UI at http://localhost:8529 in your browser and create a database.
Initially, there will be a single database called `_system`. You can create a new database by
selecting the `Databases` tab on the left pane and clicking the `Add Database` button. Use any name
you like.

### Install the Torc API service

1. Download the `torc-service.zip` file from the latest [Torc release page]
   (https://github.com/NREL/torc/releases) on GitHub. The zip file is listed under `Assets`.

2. In the web UI, switch to the database you created in the previous step. You can do this by
   selecting the database name on the `DB` selector on the top right corner of the web UI or by
   going back to the login prompt.

3. Click the `Services` tab on the left pane and click the `Add Service` button.

4. Click the `Upload` button and select the `torc-service.zip` file you downloaded in step 1.

5. Click the `Install` button to install the service.

6. Set the `Mount point` to `torc-service` and click the new `Install` button.

7. Explore the options if you'd like. The `API` tab will show you the HTTP API endpoints.
   The `Settings` tab allows you to replace the service. You'll need to do this when there are
   new releases of Torc.
