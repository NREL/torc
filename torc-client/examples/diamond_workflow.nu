#!/usr/bin/env nu

let TORC_CLIENT = $"./target/debug/torc-client"
# Set up test database
$env.DATABASE_URL = $"sqlite:(mktemp -t --suffix .db torc.XXX)"
print $env.DATABASE_URL

# Function to run command, capture JSON output, and exit on failure
def run_command_json [command: string] {
    print $"Running: ($command)"
    let result = (bash -c $command | complete)
    if $result.exit_code != 0 {
        print $"Error: Command failed with exit code ($result.exit_code)"
        print $"Command: ($command)"
        print $"stdout: ($result.stdout)"
        print $"stderr: ($result.stderr)"
        exit $result.exit_code
    }
    
    # Parse JSON output
    let json_output = ($result.stdout | from json)
    print $"Success: ($json_output)"
    return $json_output
}

# Function to run command without capturing JSON (for commands that don't return JSON)
def run_command [command: string] {
    print $"Running: ($command)"
    let result = (bash -c $command | complete)
    if $result.exit_code != 0 {
        print $"Error: Command failed with exit code ($result.exit_code)"
        print $"Command: ($command)"
        print $"stdout: ($result.stdout)"
        print $"stderr: ($result.stderr)"
        exit $result.exit_code
    }
    print $result.stdout
}

$env.DATABASE_URL = $"sqlite:(mktemp -t --suffix .db torc.XXX)"
print $env.DATABASE_URL

mut server_id = -1
let return_code = (
    try {
        cd ../server
        run_command "sqlx --no-dotenv database setup"
        run_command "cargo build --bin torc-server"
        $server_id = job spawn { ./target/debug/torc-server }
        sleep 2sec
        cd -
        print $"Started server with id: ($server_id)"
        # Build the client
        run_command "cargo build --bin torc-client"
        
        # Create workflow and capture its ID
        let workflow_result = (run_command_json $"($TORC_CLIENT) -f json workflows add -n workflow1 -d workflow1_description")
        let workflow_id = $workflow_result.id
        print $"Created workflow with ID: ($workflow_id)"
        
        # Create files and capture their IDs
        let base_input_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n base_input -p input.json")
        let base_input_id = $base_input_result.id
        
        let f1_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n f1 -p f1.json")
        let f1_id = $f1_result.id
        
        let f2_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n f2 -p f2.json")
        let f2_id = $f2_result.id
        
        let f3_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n f3 -p f3.json")
        let f3_id = $f3_result.id
        
        let f4_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n f4 -p f4.json")
        let f4_id = $f4_result.id
        
        let result_result = (run_command_json $"($TORC_CLIENT) -f json files add ($workflow_id) -n result -p result.json")
        let result_id = $result_result.id
        
        print $"Created files with IDs: base_input=($base_input_id), f1=($f1_id), f2=($f2_id), f3=($f3_id), f4=($f4_id), result=($result_id)"
        
        # Create jobs and capture their IDs
        let preprocess_result = (run_command_json $"($TORC_CLIENT) -f json jobs add ($workflow_id) -c \"bash preprocess.sh\" -n preprocess -i ($base_input_id) -o ($f1_id) -o ($f2_id)")
        let preprocess_id = $preprocess_result.id
        
        let work1_result = (run_command_json $"($TORC_CLIENT) -f json jobs add ($workflow_id) -c \"bash work.sh f1.json f3.json\" -n work1 -i ($f1_id) -o ($f3_id)")
        let work1_id = $work1_result.id
        
        let work2_result = (run_command_json $"($TORC_CLIENT) -f json jobs add ($workflow_id) -c \"bash work.sh f2.json f4.json\" -n work2 -i ($f2_id) -o ($f4_id)")
        let work2_id = $work2_result.id
        
        let postprocess_result = (run_command_json $"($TORC_CLIENT) -f json jobs add ($workflow_id) -c \"bash postprocess.sh f3.json f4.json result.json\" -n postprocess -i ($f3_id) -i ($f4_id) -o ($result_id) --blocking-job-ids ($work1_id) --blocking-job-ids ($work2_id)")
        let postprocess_id = $postprocess_result.id
        
        print $"Created jobs with IDs: preprocess=($preprocess_id), work1=($work1_id), work2=($work2_id), postprocess=($postprocess_id)"
        
        let event = (run_command_json $"($TORC_CLIENT) -f json events add ($workflow_id) -d \'{\"key1\": \"value1\"}\'")
        print $"Created event: ($event)"
        # Initialize jobs
        run_command $"($TORC_CLIENT) workflows initialize-jobs ($workflow_id)"
        
        print "Diamond workflow created successfully!"
        print $"Workflow ID: ($workflow_id)"
        print $"File IDs: base_input=($base_input_id), f1=($f1_id), f2=($f2_id), f3=($f3_id), f4=($f4_id), result=($result_id)"
        print $"Job IDs: preprocess=($preprocess_id), work1=($work1_id), work2=($work2_id), postprocess=($postprocess_id)"
        print (run_command_json $"($TORC_CLIENT) -f json events list ($workflow_id)")
        
        let response = run_command_json $"($TORC_CLIENT) -f json workflows complete-job -j ($preprocess_id) -s done -c 1 --run-id 1 --return-code 0 -e 0.5"
        print $"Complete job response: ($response)"
        let response = (run_command_json $"($TORC_CLIENT) -f json jobs get ($preprocess_id)")
        if $response.status != 'done' {
            print $"Error: Expected job status to be 'done', but got '($response.status)'"
            exit 1
        }
        let work1_response = (run_command_json $"($TORC_CLIENT) -f json jobs get ($work1_id)")
        if $work1_response.status != 'ready' {
            print $"Error: Expected work1 job status to be 'ready', but got '($work1_response.status)'"
            exit 1
        }

        let work2_response = (run_command_json $"($TORC_CLIENT) -f json jobs get ($work2_id)")
        if $work2_response.status != 'ready' {
            print $"Error: Expected work2 job status to be 'ready', but got '($work2_response.status)'"
            exit 1
        }
        run_command_json $"($TORC_CLIENT) -f json workflows complete-job -j ($work1_id) -s done -c 1 --run-id 1 --return-code 0 -e 1.5"
        run_command_json $"($TORC_CLIENT) -f json workflows complete-job -j ($work2_id) -s done -c 1 --run-id 1 --return-code 0 -e 2.5"
        let postprocess_response = (run_command_json $"($TORC_CLIENT) -f json jobs get ($postprocess_id)")
        if $postprocess_response.status != 'ready' {
            print $"Error: Expected postprocess job status to be 'ready', but got '($postprocess_response.status)'"
            exit 1
        }
        run_command($"($TORC_CLIENT) -f json workflows complete-job -j ($postprocess_id) -s done -c 1 --run-id 1 --return-code 0 -e 3.5")
        0
        
    } catch { |err|
        print $"Script failed: ($err.msg)"
        1
    }
)
if $server_id != -1 {
    job kill $server_id
    print "Terminated server"
}
print $env.DATABASE_URL
exit $return_code
