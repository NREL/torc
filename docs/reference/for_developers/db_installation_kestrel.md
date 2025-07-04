(eagle-db-installation)=

# Database Installation on Kestrel

1. Start the ArangoDB apptainer container in a directory where you want
   to keep your database. Note that you can reload your data after stopping and restarting the
   container.

```{eval-rst}
.. warning:: Do not run ArangoDB on a login node.
```

This script will acquire a node and start the database in a container. Edit the Slurm and
ArangoDB parameters as needed. ArangoDB will store its data in `arangodb3` and
`arangodb3-apps`. Reuse these directories if you start a new session later.

```console
#!/bin/bash
#SBATCH --account=my-account
#SBATCH --job-name=arangodb
#SBATCH --time=01:00:00
#SBATCH --output=output_%j.o
#SBATCH --error=output_%j.e
#SBATCH --nodes=1
#SBATCH --partition=debug

module load apptainer
apptainer run \
    --network-args "portmap=8529:8529" \
    --env "ARANGO_ROOT_PASSWORD=openSesame" \
    -B arangodb3:/var/lib/arangodb3 \
    -B arangodb3-apps:/var/lib/arangodb3-apps \
    /datasets/images/arangodb/arangodb.sif
```

Copy that text into `batch_arangod.sh` and submit it to Slurm. `tail` will print text
from `arangod` when it starts.

```console
$ sbatch batch_arangod.sh
$ tail -f output*.o
```

2. Open an SSH tunnel on your computer if you want to be able to access the web UI which is running
   on the compute node.

```console
# This example uses the node r102u34. Change it to your compute node.
$ ssh -L 8529:r102u34:8529 $USER@eagle.hpc.nrel.gov
```

3. Create a database for a workflow. You can use the web UI or `arangosh`.

```console
$ module load apptainer
$ mkdir arangodb3 arangodb3-apps
$ apptainer run \
      --network-args "portmap=8529:8529" \
      --env "ARANGO_ROOT_PASSWORD=openSesame" \
      -B arangodb3:/var/lib/arangodb3 \
      -B arangodb3-apps:/var/lib/arangodb3-apps \
      /datasets/images/arangodb/arangodb.sif \
      arangosh
```

You will be at a prompt like this:

```
127.0.0.1:8529@_system>
```

Here is the `arangosh` command to create a database. You can use any name; all examples in this
page use `workflows`.

```console
127.0.0.1:8529@_system> db._createDatabase('workflows')
```

```{raw} html
<hr>
```

4. Build the API service package from your local clone of this repository. This is probably easier
   to do on your local computer. When there is a shared directory on Eagle, this step won't be
   necessary.

```console
$ npm install
$ zip -r torc-service.zip manifest.json index.js src scripts
```

5. Use the foxx-cli apptainer container to install the API service. This can be done on a login
   node. Change the IP address to the database compute node if you are not already on that node.
   You will be prompted for your password. If you don't have authentication enabled, exclude the
   `--password` option.

```console
$ module load apptainer
$ apptainer run -B /scratch:/scratch \
    /datasets/images/arangodb/arangodb.sif foxx install \
    --server http://127.0.0.1:8529 \
    --database workflows \
    -username root \
    -password \
    /torc-service \
    /scratch/dthom/torc-service.zip
$ apptainer run -B /scratch:/scratch \
    /datasets/images/arangodb/arangodb.sif foxx set-dev \
    --server http://127.0.0.1:8529 \
    --database workflows \
    -username root \
    -password \
    --server http://127.0.0.1:8529 \
    /torc-service
```

You can install foxx-cli in your environment if you prefer, but you need `npm` installed.

```console
$ npm install --global foxx-cli
```

```{raw} html
<hr>
```

6. Test the installation.

   Test the endpoint by running this command to get an example workflow. (`jq` is not required
   but generally useful for displaying and filtering JSON output).

```console
$ curl --silent -X GET http://localhost:8529/_db/workflows/torc-service/workflow/example | jq .
```
