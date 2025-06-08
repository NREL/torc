#!/bin/bash
#SBATCH --account=dsgrid
#SBATCH --job-name=arangodb
#SBATCH --time=01:00:00
#SBATCH --output=output_%j.o
#SBATCH --error=output_%j.e
#SBATCH --nodes=1
#SBATCH --partition=debug
#SBATCH --qos=standby

module load apptainer
apptainer run \
    --network-args "portmap=8529:8529" \
    --env "ARANGO_ROOT_PASSWORD=openSesame" \
    -B arangodb3:/var/lib/arangodb3 \
    -B arangodb3-apps:/var/lib/arangodb3-apps \
    /datasets/images/arangodb/arangodb.sif
