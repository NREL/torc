# Tried version 3.0.46; it broke a bunch of things.
# TODO: debug the problems and support the latest version.
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
swap_text "s/DELETE/delete/g"
swap_text "s/GET/get/g"
swap_text "s/POST/post/g"
swap_text "s/PUT/put/g"
# Arango uses 'body' for request/response boy.
# 'model' makes more sense for items stored in the db.
swap_text "s/_body/_model/g"
rm swagger.json

if [ -z ${PYTHON_CLIENT} ]; then
    PYTHON_CLIENT=$(pwd)/python_client
fi
rm -rf ${PYTHON_CLIENT}
mkdir ${PYTHON_CLIENT}
docker run \
    -v $(pwd):/src \
    -v ${PYTHON_CLIENT}:/python_client \
    swaggerapi/swagger-codegen-cli-${SWAGGER_VERSION} \
    generate --lang=python --input-spec=/src/openapi.yaml -o /python_client -c /src/config.json

# Workaround for this issue: https://github.com/swagger-api/swagger-codegen/issues/9991
# It is fixed in the openapi-generator, but that doesn't work with our openapi.yaml - and haven't
# debugged it.
sed -i .bk "s/def __del__/def close/" ${PYTHON_CLIENT}/torc/swagger_client/api_client.py
python fix_docstring_errors.py ${PYTHON_CLIENT}/torc/swagger_client/api/default_api.py
rm -f ${PYTHON_CLIENT}/torc/swagger_client/api_client.py.bk
rm -rf ../torc_package/torc/swagger_client
mv ${PYTHON_CLIENT}/torc/swagger_client ../torc_package/torc/swagger_client
