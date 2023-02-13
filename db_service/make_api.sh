if [ -z ${SWAGGER_CODEGEN_CLI} ]; then
    echo "Please define the path to the generator in the environment variable SWAGGER_CODEGEN_CLI."
    exit 1
fi

if [ -z ${WMS_URL} ]; then
    export WMS_URL=http://localhost:8529
fi

rm -f swagger.json openapi.yaml
user="root"
if [ ! -z ${WMS_PASSWORD} ]; then
    user="${user}:${WMS_PASSWORD}"
fi
swagger=$(curl -u ${user} --silent -X GET ${WMS_URL}/_db/workflows/_admin/aardvark/foxxes/docs/swagger.json\?mount\=%2Fwms-service)
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
swap_text "s/hpc_configs_body/hpc_config_model/g"
swap_text "s/files_body/file_model/g"
swap_text "s/results_body/result_model/g"
swap_text "s/compute_nodes_body/compute_nodes_model/g"
swap_text "s/jobs_body/job_model/g"
swap_text "s/job_definitions_body/job_definition/g"
swap_text "s/resource_requirements_body/resource_requirements_model/g"
swap_text "s/edges_name_body/edge_model/g"
swap_text "s/workflow_body/workflow/g"
swap_text "s/workflow_jobs/job_definition2/g"  # Is there a way to eliminate the duplicate?
swap_text "s/workflow_prepare_jobs_for_submission_body/worker_resources/g"
rm swagger.json

python_dir=python_client
rm -rf $python_dir
mkdir $python_dir
java -jar ${SWAGGER_CODEGEN_CLI} generate --lang=python --input-spec=openapi.yaml -o $python_dir
