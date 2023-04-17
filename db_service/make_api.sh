if [ -z ${SWAGGER_CODEGEN_CLI} ]; then
    echo "Please define the path to the generator in the environment variable SWAGGER_CODEGEN_CLI."
    exit 1
fi

if [ -z ${TORC_URL} ]; then
    export TORC_URL=http://localhost:8529
fi

rm -f swagger.json openapi.yaml
user="root"
if [ ! -z ${TORC_PASSWORD} ]; then
    user="${user}:${TORC_PASSWORD}"
fi
swagger=$(curl -u ${user} --silent -X GET ${TORC_URL}/_db/test-workflows/_admin/aardvark/foxxes/docs/swagger.json\?mount\=%2Ftorc-service)
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

java -jar ${SWAGGER_CODEGEN_CLI} generate --lang=openapi-yaml --input-spec=swagger.json
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
    PYTHON_CLIENT=./python_client
fi
rm -rf ${PYTHON_CLIENT}
mkdir ${PYTHON_CLIENT}
java -jar ${SWAGGER_CODEGEN_CLI} generate --lang=python --input-spec=openapi.yaml -o ${PYTHON_CLIENT}
# Workaround for this issue: https://github.com/swagger-api/swagger-codegen/issues/9991
# It is fixed in the openapi-generator, but that doesn't work with our openapi.yaml - and haven't
# debugged it.
sed -i .bk "s/def __del__/def close/" ${PYTHON_CLIENT}/swagger_client/api_client.py
rm -f ${PYTHON_CLIENT}/swagger_client/api_client.py.bk
