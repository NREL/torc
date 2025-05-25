(local-db-installation)=

# Local Database Installation

## Database Installation

Choose how you want to run ArangoDB: natively or in a container.

### Native installation

1\. Install `ArangoDB Community Edition` locally by following instructions at
<https://www.arangodb.com/download-major/>

Add the `bin` directory to your system path. It will likely be in a location like this:

```
$HOME/Applications/ArangoDB3-CLI.app/Contents/Resources/opt/arangodb/bin
```

Note the configuration files in this directory:

```
$HOME/Applications/ArangoDB3-CLI.app/Contents/Resources/opt/arangodb/etc/arangodb3
```

Customize as desired, particularly regarding authentication.

2. Start the database by running `arangodb`.

You may need to specify the config file with `arangodb --conf <your-path>/arangod.conf`

```{raw} html
<hr>
```

### Docker container

Run the ArangoDB Docker container by following instructions at
<https://www.arangodb.com/download-major/docker/>

```{raw} html
<hr>
```

## foxx CLI

Regardless of native install vs Docker, install the ArangoDB CLI tool `foxx-cli`
locally as described at <https://github.com/arangodb/foxx-cli>. This is used to manage API services.

```{raw} html
<hr>
```

## Configure the database

Verify the installation by logging into the ArangoDB web server at <http://localhost:8529>
on your browser. You can also use Arango's JavaScript REPL via `arangosh`.

```{eval-rst}
.. note:: The default username/password used by the container instructions is ``root/openSesame``.
```

Create a database in the web UI or `arangosh`.

```{raw} html
<hr>
```

Run `arangosh` in the terminal. If you installed locally, it will be in the same location as
`arangod`.

You will be at a prompt like this:

```
127.0.0.1:8529@_system>
```

Here is the `arangosh` command to create a database. You can use any name; all examples in this
page use `workflows`. Note that the name shows up in the the API endpoint that you'll create
in the next step.

```{eval-rst}
.. note:: If you want to run the torc test suite, the database name must be ``test-workflows``.
```

```console
127.0.0.1:8529@_system> db._createDatabase('workflows')
```

```{raw} html
<hr>
```

### API Service

Create the service that will implement the API endpoint. Change to the `db_service` directory
after cloning this repository.

```console
$ npm install
$ zip -r torc-service.zip manifest.json index.js src scripts node_modules
```

Install that service via the web app by following instructions at
<https://www.arangodb.com/docs/stable/foxx-getting-started.html#try-it-out> or by using the `foxx`
CLI application. CLI instructions are at <https://github.com/arangodb/foxx-cli>.

When developing the API, use `foxx` because you will need to update the service continually.

```{raw} html
<hr>
```

#### foxx configuration instructions

Default `foxx` instructions didn't fully work. Here are some that did:

1. Create an alias for a `dev` server.

```console
$ foxx server set dev http://127.0.0.1:8529 -D workflows -u root
```

2. Set the password if you have authentication enabled.

```console
$ cat ~/.foxxrc
[server.dev]
 url=http://127.0.0.1:8529
 database=workflows
 username=root
 password=my_password
```

3. Confirm the installation.

```console
$ foxx list --server dev
  /torc-service           [DEV]
```

4. Install the service.

```console
$ foxx install -H dev /torc-service torc-service.zip
```

You can replace an existing service with

```console
$ foxx replace -H dev /torc-service torc-service.zip
```

5\. Enable development mode with this command (this can also be done in the settings tab of the web
UI)

```console
$ foxx set-dev --server dev /torc-service
```

Be sure to read <https://www.arangodb.com/docs/stable/foxx-guides-development-mode.html> when
developing the API endpoint.

```{raw} html
<hr>
```

## Test the installation

Test the endpoint by running this command to get an example workflow. (`jq` is not required but
generally useful for displaying and filtering JSON output).

```console
$ curl --silent -X GET http://localhost:8529/_db/workflows/torc-service/workflow/example | jq .
```
