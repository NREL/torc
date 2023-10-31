# This will become 7.1.0 whenever that is released (to support pydantic v2).
OPENAPI_CLI_VERSION=latest
SWAGGER_CLI_VERSION=v3:3.0.36

set -x
set -e

if [ -z ${CONTAINER_EXEC} ]; then
    CONTAINER_EXEC=docker
fi

if [ -z ${TORC_DATABASE_NAME} ]; then
    TORC_DATABASE_NAME=test-workflows
fi

if [ -z ${TORC_URL} ]; then
    TORC_URL=http://localhost:8529
fi

if [ -z ${TORC_USER} ]; then
    TORC_USER=root
fi

rm -f swagger.json openapi.yaml
if [ -z ${TORC_PASSWORD} ]; then
    user=${TORC_USER}:openSesame
else
    user="${TORC_USER}:${TORC_PASSWORD}"
fi
swagger=$(curl -u ${user} --silent -X GET ${TORC_URL}/_db/${TORC_DATABASE_NAME}/_admin/aardvark/foxxes/docs/swagger.json\?mount\=%2Ftorc-service)
error=$(echo "${swagger}" | jq '.error')
if [[ ${error} == true ]]; then
    echo "${swagger}" | jq .
    exit 1
fi

function swap_text()
{
    sed -i.bk "$1" openapi.yaml
    rm openapi.yaml.bk
}

echo "$swagger" | jq . > swagger.json


if [ ! -z ${LOCAL_SWAGGER_CODEGEN_CLI} ]; then
    # This docker container below doesn't work on Macs with M1 or M2 processors.
    # Those users need to download
    # https://mvnrepository.com/artifact/io.swagger.codegen.v3/swagger-codegen-cli/3.0.36
    # and set this environment variable.
    # TODO: find a better solution.
    java -jar ${LOCAL_SWAGGER_CODEGEN_CLI} \
        generate --lang=openapi-yaml --input-spec=swagger.json -o .
else
    ${CONTAINER_EXEC} run \
        -v $(pwd):/data \
        docker.io/swaggerapi/swagger-codegen-cli-${SWAGGER_CLI_VERSION} \
        generate --lang=openapi-yaml --input-spec=/data/swagger.json -o /data
fi

rm swagger.json
python fix_openapi_spec.py openapi.yaml

if [ -z ${PYTHON_CLIENT} ]; then
    PYTHON_CLIENT=$(pwd)/python_client
fi
rm -rf ${PYTHON_CLIENT}
mkdir ${PYTHON_CLIENT}

if [ -z ${JULIA_CLIENT} ]; then
    JULIA_CLIENT=$(pwd)/julia_client
fi
rm -rf ${JULIA_CLIENT}
mkdir ${JULIA_CLIENT}

${CONTAINER_EXEC} run \
    -v $(pwd):/data \
    -v ${PYTHON_CLIENT}:/python_client \
    docker.io/openapitools/openapi-generator-cli:${OPENAPI_CLI_VERSION} \
    generate -g python --input-spec=/data/openapi.yaml -o /python_client -c /data/config.json

${CONTAINER_EXEC} run \
    -v $(pwd):/data \
    -v ${JULIA_CLIENT}:/julia_client \
    docker.io/openapitools/openapi-generator-cli:latest \
    generate -g julia-client --input-spec=/data/openapi.yaml -o /julia_client

rm -rf ../torc_package/torc/openapi_client
rm -rf ../julia/Torc/src/api
rm -rf ../julia/julia_client/docs
rm ../julia/julia_client/README.md
mv ${PYTHON_CLIENT}/torc/openapi_client ../torc_package/torc/openapi_client
mv ${JULIA_CLIENT}/src ../julia/Torc/src/api
mv ${JULIA_CLIENT}/docs ../julia/julia_client/
mv ${JULIA_CLIENT}/README.md ../julia/julia_client/
