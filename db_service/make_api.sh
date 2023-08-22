SWAGGER_VERSION=v3:3.0.36

if [ -z ${TORC_DATABASE_NAME} ]; then
    echo "Please define the database name in the environment variable TORC_DATABASE_NAME."
    exit 1
fi

if [ -z ${TORC_URL} ]; then
    TORC_URL=http://localhost:8529
fi

if [ -z ${TORC_USER} ]; then
    TORC_USER=root
fi

rm -f swagger.json openapi.yaml
if [ -z ${TORC_PASSWORD} ]; then
    user=${TORC_USER}
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
    sed -i .bk "$1" openapi.yaml
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "sed failed: $ret"
        exit 1
    fi
    rm openapi.yaml.bk
}

echo "$swagger" | jq . > swagger.json

docker run \
    -v $(pwd):/src \
    swaggerapi/swagger-codegen-cli-${SWAGGER_VERSION} \
    generate --lang=openapi-yaml --input-spec=/src/swagger.json -o /src

ret=$?
if [ $ret -ne 0 ]; then
    echo "Failed to convert swagger.json to openapi.yaml"
    exit 1
fi
rm swagger.json
python fix_openapi_spec.py openapi.yaml
if [ $? -ne 0 ]; then
    echo "Failed to fix the openapi specification"
    exit 1
fi

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

# TODO: 7.0.0 version is not finalized, but seems to be required for what we're doing. 6.6.0 failed
# Python client. It seems to add lots of good stuff, like using Pydantic for the backing data models.
# Use the 'latest' tag. The release should be in Aug 2023.
docker run \
    -v $(pwd):/src \
    -v ${PYTHON_CLIENT}:/python_client \
    openapitools/openapi-generator-cli \
    generate -g python --input-spec=/src/openapi.yaml -o /python_client -c /src/config.json
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

docker run \
    -v $(pwd):/src \
    -v ${JULIA_CLIENT}:/julia_client \
    openapitools/openapi-generator-cli \
    generate -g julia-client --input-spec=/src/openapi.yaml -o /julia_client
if [ $? -ne 0 ]; then
    echo "Failed to build the julia client"
    exit 1
fi

rm -rf ../torc_package/torc/openapi_client
rm -rf ../julia/Torc/src/api
rm -rf ../julia/julia_client/docs
rm ../julia/julia_client/README.md
mv ${PYTHON_CLIENT}/torc/openapi_client ../torc_package/torc/openapi_client
mv ${JULIA_CLIENT}/src ../julia/Torc/src/api
mv ${JULIA_CLIENT}/docs ../julia/julia_client/
mv ${JULIA_CLIENT}/README.md ../julia/julia_client/
