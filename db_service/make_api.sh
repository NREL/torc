OPENAPI_CLI_VERSION=v7.0.0
SWAGGER_CLI_VERSION=v3:3.0.36

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

rm -f db_service/swagger.json db_service/openapi.yaml
if [ -z ${TORC_PASSWORD} ]; then
    user=${TORC_USER}:openSesame
else
    user="${TORC_USER}:${TORC_PASSWORD}"
fi
swagger=$(curl -u ${user} --silent -X GET ${TORC_URL}/_db/${TORC_DATABASE_NAME}/_admin/aardvark/foxxes/docs/swagger.json\?mount\=%2Ftorc-service)
ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to download swagger.json"
    exit 1
fi
error=$(echo "${swagger}" | jq '.error')
if [[ ${error} == true ]]; then
    echo "${swagger}" | jq .
    exit 1
fi

function swap_text()
{
    sed -i .bk "$1" db_service/openapi.yaml
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "sed failed: $ret"
        exit 1
    fi
    rm db_service/openapi.yaml.bk
}

echo "$swagger" | jq . > db_service/swagger.json


if [ ! -z ${LOCAL_SWAGGER_CODEGEN_CLI} ]; then
    # This docker container below doesn't work on Macs with M1 or M2 processors.
    # Those users need to download
    # https://mvnrepository.com/artifact/io.swagger.codegen.v3/swagger-codegen-cli/3.0.36
    # and set this environment variable.
    # TODO: find a better solution.
    java -jar ${LOCAL_SWAGGER_CODEGEN_CLI} \
        generate --lang=openapi-yaml --input-spec=db_service/swagger.json -o .
else
    ${CONTAINER_EXEC} run \
        -v $(pwd)/db_service:/db_service \
        docker.io/swaggerapi/swagger-codegen-cli-${SWAGGER_CLI_VERSION} \
        generate --lang=openapi-yaml --input-spec=/db_service/swagger.json -o /db_service
fi

ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to convert swagger.json to openapi.yaml"
    exit 1
fi
rm db_service/swagger.json
python db_service/fix_openapi_spec.py db_service/openapi.yaml
if [ $? -ne 0 ]; then
    echo "Failed to fix the openapi specification"
    exit 1
fi

if [ -z ${PYTHON_CLIENT} ]; then
    PYTHON_CLIENT=$(pwd)/db_service/python_client
fi
rm -rf ${PYTHON_CLIENT}
mkdir ${PYTHON_CLIENT}

if [ -z ${JULIA_CLIENT} ]; then
    JULIA_CLIENT=$(pwd)/db_service/julia_client
fi
rm -rf ${JULIA_CLIENT}
mkdir ${JULIA_CLIENT}

${CONTAINER_EXEC} run \
    -v $(pwd)/db_service:/db_service \
    -v ${PYTHON_CLIENT}:/python_client \
    docker.io/openapitools/openapi-generator-cli:${OPENAPI_CLI_VERSION} \
    generate -g python --input-spec=/db_service/openapi.yaml -o /python_client -c /db_service/config.json
if [ $? -ne 0 ]; then
    echo "Failed to build the python client ***"
    exit 1
fi

cd ${PYTHON_CLIENT}
bump-pydantic torc
if [ $? -ne 0 ]; then
    echo "Failed to convert OpenAPI pydantic models."
    exit 1
fi
cd -
# Fix pydantic methods that are deprecated in v2.
find ${PYTHON_CLIENT}/torc -name "*.py" -exec sed -i .bk "s/parse_obj/model_validate/g" {} \;
find ${PYTHON_CLIENT}/torc -name "*.py" -exec sed -i .bk "s/validate_arguments/validate_call/g" {} \;
find ${PYTHON_CLIENT}/torc -name "*.py" -exec sed -i .bk "s/self.dict(/self.model_dump(/g" {} \;
find ${PYTHON_CLIENT}/torc -name "*.bk" -exec rm {} \;

${CONTAINER_EXEC} run \
    -v $(pwd)/db_service:/db_service \
    -v ${JULIA_CLIENT}:/julia_client \
    openapitools/openapi-generator-cli \
    generate -g julia-client --input-spec=/db_service/openapi.yaml -o /julia_client
if [ $? -ne 0 ]; then
    echo "Failed to build the julia client"
    exit 1
fi

rm -rf torc_package/torc/openapi_client
rm -rf julia/Torc/src/api
rm -rf julia/julia_client/docs
rm julia/julia_client/README.md
mv ${PYTHON_CLIENT}/torc/openapi_client torc_package/torc/openapi_client
mv ${JULIA_CLIENT}/src julia/Torc/src/api
mv ${JULIA_CLIENT}/docs julia/julia_client/
mv ${JULIA_CLIENT}/README.md julia/julia_client/
