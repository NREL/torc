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
swap_text "s/aws_schedulers_body/aws_schedulers_model/g"
swap_text "s/aws_schedulers_key_body/aws_schedulers_key_model/g"
swap_text "s/compute_node_stats_body/compute_node_stats_model/g"
swap_text "s/compute_node_stats_key_body/compute_node_stats_key_model/g"
swap_text "s/compute_nodes_body/compute_nodes_model/g"
swap_text "s/compute_nodes_key_body/compute_nodes_key_model/g"
swap_text "s/edges_name_body/edge_model/g"
swap_text "s/files_body/file_model/g"
swap_text "s/files_key_body/files_key_model/g"
swap_text "s/job_definitions_body/job_definition/g"
swap_text "s/jobs_key_body/jobs_key_model/g"
swap_text "s/job_process_stats_body/job_process_stats_model/g"
swap_text "s/job_process_stats_key_body/job_process_stats_key_model/g"
swap_text "s/jobs_body/job_model/g"
swap_text "s/local_schedulers_body/local_schedulers_model/g"
swap_text "s/local_schedulers_key_body/local_schedulers_key_model/g"
swap_text "s/resource_requirements_body/resource_requirements_model/g"
swap_text "s/resource_requirements_key_body/resource_requirements_key_model/g"
swap_text "s/results_body/result_model/g"
swap_text "s/results_key_body/results_key_model/g"
swap_text "s/status_rev_body/status_rev_model/g"
swap_text "s/slurm_schedulers_body/slurm_schedulers_model/g"
swap_text "s/slurm_schedulers_key_body/slurm_schedulers_key_model/g"
swap_text "s/store_user_data_key_body/store_user_data_key_model/g"
swap_text "s/workflow_body/workflow_model/g"
swap_text "s/workflow_config_body/workflow_config_model/g"
swap_text "s/workflow_config_key_body/workflow_config_key_model/g"
swap_text "s/workflow_prepare_jobs_for_submission_body/workflow_prepare_jobs_for_submission_model/g"
rm swagger.json

python_dir=python_client
rm -rf $python_dir
mkdir $python_dir
java -jar ${SWAGGER_CODEGEN_CLI} generate --lang=python --input-spec=openapi.yaml -o $python_dir
